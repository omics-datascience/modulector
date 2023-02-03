import re
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

        # Gets genes aliases
        gene_aliases = self.__get_gene_aliases(gene)

        # Gets miRNAs aliases
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


class MirnasFinder(APIView):
    """Service that takes a string of any length and returns a list of miRNAs' ids that contain that search criteria."""

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


class MethylationSite(APIView):
    """Service that searches the identifier of a methylation site from different versions of Illumina arrays and
    returns the identifier of the most recent version."""

    @staticmethod
    def get(_request, input_id: str):
        res = MethylationEPIC.objects.filter(Q(ilmnid=input_id) | Q(name=input_id) |
                                             Q(methyl450_loci=input_id) | Q(methyl27_loci=input_id) |
                                             Q(epicv1_loci=input_id)).values_list('name', flat=True)

        return Response({input_id: list(res)})


class MethylationSites(APIView):
    """Service that searches a list of methylation site identifiers from different Illumina array versions and
    returns the identifiers for the most recent version of the array."""

    @staticmethod
    def post(request):
        data = request.data
        if "genes_ids" not in data:
            return Response("'genes_ids' is mandatory", status=status.HTTP_400_BAD_REQUEST)

        genes_ids = data["genes_ids"]
        if type(genes_ids) != list:
            return Response("'genes_ids' must be of list type", status=status.HTTP_400_BAD_REQUEST)

        res = {}
        for gene_id in genes_ids:
            # TODO: instead of calling this request, it should be a common function to get the data
            res[gene_id] = MethylationSite.get(request, gene_id).data[gene_id]

        return Response(res)

        # res = MethylationEPIC.objects.filter(Q(ilmnid=input_id) | Q(name=input_id) |
        #                                      Q(methyl450_loci=input_id) | Q(methyl27_loci=input_id) |
        #                                      Q(epicv1_loci=input_id)).values_list('name', flat=True)
        #
        # return Response({input_id: list(res)})


class MethylationsFinder(APIView):
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
