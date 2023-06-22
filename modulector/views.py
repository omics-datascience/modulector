import re
from concurrent.futures import ProcessPoolExecutor
from typing import List, Optional
from django.conf import settings
from django.db.models.query_utils import Q
from django.http import Http404
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, filters, viewsets
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView
from modulector.models import MirnaXGene, Mirna, MirbaseIdMirna, MirnaDisease, MirnaDrug, GeneAliases, MethylationEPIC
from modulector.pagination import StandardResultsSetPagination
from modulector.serializers import MirnaXGenSerializer, MirnaSerializer, \
    MirnaAliasesSerializer, MirnaDiseaseSerializer, MirnaDrugsSerializer, get_mirna_from_accession, \
    get_mirna_aliases
from modulector.services import subscription_service

regex = re.compile(r'-\d[a-z]')

# Default page size for requests
DEFAULT_PAGE_SIZE: int = 50

# Maximum page size for requests
MAX_PAGE_SIZE: int = 3000

# Number of processes to use in Pool
PROCESS_POOL_WORKERS = settings.PROCESS_POOL_WORKERS


def get_methylation_epic_sites(input_id: str) -> List[str]:
    """
    Gets methylation sites from any type of Loci id.
    :param input_id: String to query in the DB.
    :return: List of Methylation sites.
    """
    res = MethylationEPIC.objects.filter(Q(ilmnid=input_id) | Q(name=input_id) |
                                         Q(methyl450_loci=input_id) | Q(methyl27_loci=input_id) |
                                         Q(epicv1_loci=input_id)).values_list('name', flat=True)

    return list(res)


def get_limit_parameter(value: Optional[str]) -> int:
    """
    Gets a valid int value for the 'limit' parameter in requests
    :param value: Current value in GET request
    :return: Int value or the maximum value possible in case it's higher
    """
    if value is None:
        return DEFAULT_PAGE_SIZE

    try:
        int_value = int(value)
        return min(int_value, MAX_PAGE_SIZE)
    except ValueError:
        # Returns default in case of non-numeric parameter
        return DEFAULT_PAGE_SIZE


class MirnaTargetInteractions(viewsets.ReadOnlyModelViewSet):
    """Returns a single instance with data about an interaction between a miRNA and a gene
    (mirna-target-interactions endpoint)"""
    serializer_class = MirnaXGenSerializer
    handler400 = 'rest_framework.exceptions.bad_request'

    @staticmethod
    def __get_gene_aliases(gene: str) -> List[str]:
        """Retrieves the aliases for a gene based on the gene provided"""
        match_gene = GeneAliases.objects.filter(Q(alias=gene) | Q(gene_symbol=gene)).first()
        if match_gene is None:
            return []

        gene_symbol = match_gene.gene_symbol
        aliases = list(GeneAliases.objects.filter(gene_symbol=gene_symbol).values_list('alias', flat=True).distinct())
        aliases.append(gene)  # Adds the parameter to not omit it in the future search
        return aliases

    def list(self, request, *args, **kwargs):
        mirna = self.request.GET.get("mirna")
        gene = self.request.GET.get("gene")

        if not mirna or not gene:
            raise ParseError(detail="mirna and gene are obligatory")

        # Gets gene aliases
        gene_aliases = self.__get_gene_aliases(gene)

        # Gets miRNA aliases
        mirna_aliases = get_mirna_aliases(mirna)
        instance = generics.get_object_or_404(MirnaXGene, mirna__mirna_code__in=mirna_aliases, gene__in=gene_aliases)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MirnaInteractions(generics.ListAPIView):
    """Returns a paginated response with all the interactions of a specific miRNA (mirna-interactions endpoint)"""
    serializer_class = MirnaXGenSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['gene', 'score']
    ordering = ['id']
    search_fields = ['gene']
    handler400 = 'rest_framework.exceptions.bad_request'

    def get_queryset(self):
        mirna = self.request.GET.get("mirna")

        if not mirna:
            raise ParseError(detail="mirna is obligatory")

        mirna_aliases = get_mirna_aliases(mirna)
        return MirnaXGene.objects.filter(mirna__mirna_code__in=mirna_aliases)


class MirnaAliasesList(generics.ListAPIView):
    """mirna-aliases endpoint"""
    serializer_class = MirnaAliasesSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering = ['mature_mirna']
    filterset_fields = ['mature_mirna', 'mirbase_accession_id']

    def get_queryset(self):
        return MirbaseIdMirna.objects.all()


class MirnaCodes(APIView):
    """Service that searches a list of miRNA codes and returns the code for the miRbase DB."""

    @staticmethod
    def __get_mirna_code(mirna_code: str) -> Optional[str]:
        """
        Receives a miRNA Previous ID or Accession ID, and returns the associated Accession ID.
        :param mirna_code: miRNA Previous ID or Accession ID.
        :return: The associated Accession ID.
        """
        res = MirbaseIdMirna.objects.filter(Q(mirbase_accession_id=mirna_code) | Q(mature_mirna=mirna_code)).first()
        if res:
            return res.mirbase_accession_id
        else:
            return None

    def post(self, request):
        data = request.data
        if "mirna_codes" not in data:
            return Response({"detail": "'mirna_codes' is mandatory"}, status=status.HTTP_400_BAD_REQUEST)

        mirna_codes = data["mirna_codes"]
        if type(mirna_codes) != list:
            return Response({"detail": "'mirna_codes' must be of list type"}, status=status.HTTP_400_BAD_REQUEST)

        res = {}
        for mirna_id in mirna_codes:
            res[mirna_id] = self.__get_mirna_code(mirna_id)

        return Response(res)


class MirnaCodesFinder(APIView):
    """Service that takes a string of any length and returns a list of miRNA ids that contain that search criteria."""

    def get(self, _request):
        query = self.request.GET.get('query')
        if query is None:
            return Response([])

        res = []
        limit = self.request.GET.get('limit')
        limit = get_limit_parameter(limit)

        res_mirna = Mirna.objects.filter(mirna_code__istartswith=query)[:limit].values_list('mirna_code', flat=True)
        res.extend(res_mirna)
        res_mirna_count = len(res_mirna)
        if res_mirna_count < limit:
            num_of_reg = limit - res_mirna_count
            res_mirbaseidmirna_id = MirbaseIdMirna.objects.filter(mature_mirna__istartswith=query)[
                                    :num_of_reg].values_list('mature_mirna', flat=True)
            res.extend(res_mirbaseidmirna_id)
            res = list(set(res))  # Removes duplicates
            res_mirna_count = len(res_mirbaseidmirna_id)
            if res_mirna_count < limit:
                num_of_reg = limit - res_mirna_count
                res_mirbaseidmirna_acc = MirbaseIdMirna.objects.filter(mirbase_accession_id__istartswith=query)[
                                         :num_of_reg].values_list('mirbase_accession_id', flat=True)
                res.extend(res_mirbaseidmirna_acc)
                res = list(set(res))  # remove duplicates

        return Response(list(res))


class MirnaList(viewsets.ReadOnlyModelViewSet):
    """Returns a single instance of miRNA with general data (mirna endpoint)"""
    serializer_class = MirnaSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        mirna = self.request.GET.get("mirna")
        if not mirna:
            raise Http404
        aliases = get_mirna_aliases(mirna)
        instance = generics.get_object_or_404(Mirna, mirna_code__in=aliases)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        mirna = self.request.GET.get("mirna")
        if mirna:
            aliases = get_mirna_aliases(mirna)
            return generics.get_object_or_404(Mirna, mirna_code__in=aliases)
        else:
            raise Http404


class MirnaDiseaseList(generics.ListAPIView):
    """Diseases endpoint"""
    serializer_class = MirnaDiseaseSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['disease']
    ordering = ['id']
    search_fields = ['disease']

    def get_queryset(self):
        mirna = self.request.GET.get("mirna")

        result = MirnaDisease.objects.all()
        if mirna:
            if mirna.startswith('MI'):
                mirna = get_mirna_from_accession(mirna)
                result = result.filter(mirna__in=mirna)
            else:
                # This regex is implemented in case that we received a mature mirna
                # that also -5p or -3p (for example) suffix, we remove it to search
                if mirna.count('-') == 3:
                    mirna = re.sub(regex, "", mirna)
                result = result.filter(mirna__contains=mirna)
        return result


class MirnaDrugsList(generics.ListAPIView):
    """Drugs endpoint"""
    serializer_class = MirnaDrugsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    ordering_fields = ['condition', 'detection_method', 'small_molecule', 'expression_pattern', 'reference',
                       'support']
    ordering = ['id']
    search_fields = ['condition', 'small_molecule', 'expression_pattern']
    filterset_fields = ['fda_approved']

    def get_queryset(self):
        mirna = self.request.GET.get("mirna")
        query_set = MirnaDrug.objects.all()
        if mirna:
            if mirna.startswith('MI'):
                mirna = get_mirna_from_accession(mirna)
                query_set = query_set.filter(mature_mirna__in=mirna)

            query_set = query_set.filter(mature_mirna__contains=mirna)
        return query_set


class SubscribeUserToPubmed(APIView):
    @staticmethod
    def get(request):
        email = request.GET.get("email")
        mirna = request.GET.get("mirna")
        gene = request.GET.get("gene")
        token = subscription_service.subscribe_user(email=email, mirna=mirna, gene=gene)
        return Response({'token': token}, status=status.HTTP_200_OK)


class UnsubscribeUserToPubmed(APIView):
    @staticmethod
    def get(request):
        token = request.GET.get("token")
        subscription_service.unsubscribe_user(token=token)
        return Response("Your subscription has been deleted", status=status.HTTP_200_OK)


class MethylationSites(APIView):
    """Service that searches a list of methylation site identifiers from different Illumina array versions and
    returns the identifiers for the most recent version of the array."""
    @staticmethod
    def post(request):
        data = request.data
        if "methylation_sites" not in data:
            return Response({"detail": "'methylation_sites' is mandatory"}, status=status.HTTP_400_BAD_REQUEST)

        methylation_sites = data["methylation_sites"]
        if type(methylation_sites) != list:
            return Response({"detail": "'methylation_sites' must be of list type"}, status=status.HTTP_400_BAD_REQUEST)

        # Generates a dict with the methylation sites as keys and the result of the query as values.
        # NOTE: it uses ProcessPoolExecutor to parallelize the queries and not a ThreadPoolExecutor because
        # the latter has a bug closing Django connections (see https://stackoverflow.com/q/57211476/7058363)
        with ProcessPoolExecutor(max_workers=PROCESS_POOL_WORKERS) as executor:
            res = {
                methylation_name: result
                for methylation_name, result in zip(methylation_sites, executor.map(
                        get_methylation_epic_sites, methylation_sites
                ))
            }

        return Response(res)


class MethylationSitesFinder(APIView):
    """Service that takes a text string of any length and returns a list of methylation site names (loci) containing
    that search criteria within the Illumina 'Infinium MethylationEPIC' array."""

    def get(self, _request):
        query = self.request.GET.get('query')
        if query is None:
            return Response([])

        limit = self.request.GET.get('limit')
        limit = get_limit_parameter(limit)

        res = MethylationEPIC.objects.filter(name__istartswith=query)[:limit].values_list('name', flat=True)
        return Response(list(res))


def index(request):
    return render(request, 'index.html', {'version': settings.VERSION})
