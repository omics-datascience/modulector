import re
from typing import Final

from django.conf import settings
from django.db.models.query_utils import Q
from django.http import Http404, HttpRequest
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, filters, viewsets
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView
from modulector.models import MethylationUCSC_CPGIsland, MethylationUCSCRefGene, MirnaXGene, Mirna, MirbaseIdMirna, \
    MirnaDisease, MirnaDrug, GeneAliases, MethylationEPIC
from modulector.pagination import StandardResultsSetPagination
from modulector.serializers import MirnaXGenSerializer, MirnaSerializer, \
    MirnaAliasesSerializer, MirnaDiseaseSerializer, MirnaDrugsSerializer, get_mirna_from_accession, \
    get_mirna_aliases
from modulector.services import subscription_service
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


regex = re.compile(r'-\d[a-z]')

# Default page size for requests
DEFAULT_PAGE_SIZE: Final[int] = 50

# Maximum page size for requests
MAX_PAGE_SIZE: Final[int] = 3000

# Number of processes to use in Pool
PROCESS_POOL_WORKERS: Final[int] = settings.PROCESS_POOL_WORKERS


def get_methylation_match_condition(input_name: str) -> Q:
    """Generates the condition to match a Methylation site."""
    return (Q(ilmnid=input_name) | Q(name=input_name) | Q(methyl450_loci=input_name) | Q(methyl27_loci=input_name) |
            Q(epicv1_loci=input_name))


def get_methylation_epic_sites_names(input_id: str) -> tuple[str, list[str]]:
    """
    Gets methylation sites from any type of Loci id.
    :param input_id: String to query in the DB.
    :return: list of Methylation sites.
    """
    condition = get_methylation_match_condition(input_id)
    res = MethylationEPIC.objects.filter(condition).values_list('name', flat=True)

    return input_id, list(res)


def get_limit_parameter(value: str | None) -> int:
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


class MirnaTargetInteractions(generics.ListAPIView):
    """Returns a paginated response with all the interactions of a specific miRNA (mirna-interactions endpoint)"""
    serializer_class = MirnaXGenSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['gene', 'score']
    ordering = ['id']
    handler400 = 'rest_framework.exceptions.bad_request'

    @staticmethod
    def __get_gene_aliases(gene: str) -> list[str]:
        """Retrieves the aliases for a gene based on the gene provided"""
        match_gene = GeneAliases.objects.filter(
            Q(alias=gene) | Q(gene_symbol=gene)).first()
        if match_gene is None:
            return []

        gene_symbol = match_gene.gene_symbol
        aliases = list(GeneAliases.objects.filter(
            gene_symbol=gene_symbol).values_list('alias', flat=True).distinct())
        # Adds the parameter to not omit it in the future search
        aliases.append(gene)
        return aliases

    def get_serializer_context(self):
        context = super(MirnaTargetInteractions, self).get_serializer_context()

        include_pubmeds = self.request.GET.get("include_pubmeds") == "true"
        context['include_pubmeds'] = include_pubmeds
        return context

    @extend_schema(
        tags=["miRNA"],
        summary="Retrieve miRNA interactions",
        parameters=[
            OpenApiParameter(name='mirna', type=str, 
                             description='miRNA (Accession ID or name in mirBase) to get its interactions with different gene targets.',
                             required=True, 
                             examples=[
                                 OpenApiExample(name="hsa-miR-891a-5p", value="hsa-miR-891a-5p"),
                                 OpenApiExample(name="hsa-miR-891a-3p", value="hsa-miR-891a-3p")
                             ]),
            OpenApiParameter(name='gene', type=str, 
                             description='Gene symbol to get its interactions with different miRNA targets', 
                             required=False,
                             examples=[
                                OpenApiExample(name="EGFR", value="EGFR"),
                                OpenApiExample(name="APPBP2", value="APPBP2")
                             ]),
            OpenApiParameter(name='score', type=float,
                             description='Numerical score to filter the interactions (only interactions with a score greater than or equal to the parameter value are returned).',
                             required=False),
            OpenApiParameter(name='include_pubmeds', type=bool, description='If True, the endpoint also returns a list of links to Pubmed where the miRNAs are related to the genes (this may affect Modulector\'s response time)',
                             required=False),
            # Exclude pagination and ordering parameters
            OpenApiParameter(name='ordering', exclude=True),
            OpenApiParameter(name='page', exclude=True),
            OpenApiParameter(name='page_size', exclude=True)
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Receives a miRNA and/or a gene symbol and returns a paginated vector. Each vector entry represents a miRNA-Gene interaction. If no gene symbol is entered, all miRNA interactions are returned. If a miRNA is not entered, all gene interactions are returned. If both are entered, the interaction of mirna with the gene is returned.
        """
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        mirna = self.request.GET.get("mirna")
        gene = self.request.GET.get("gene")
        score = self.request.GET.get("score")

        if score:
            try:
                score = float(score)
                if not 0 <= score <= 1:
                    raise ParseError(
                        detail="the 'score' value must be between 0 and 1")
            except ValueError:
                raise ParseError(
                    detail="'score' must be a numerical value between 0 and 1")

        if not mirna and not gene:
            raise ParseError(detail="'mirna' or 'gene' are mandatory")
        elif mirna and not gene:  # only mirna
            mirna_aliases = get_mirna_aliases(mirna)
            data = MirnaXGene.objects.filter(
                mirna__mirna_code__in=mirna_aliases)
        elif not mirna and gene:  # only gene
            gene_aliases = self.__get_gene_aliases(gene)
            data = MirnaXGene.objects.filter(gene__in=gene_aliases)
        else:  # mirna and gene
            # Gets gene aliases
            gene_aliases = self.__get_gene_aliases(gene)
            # Gets miRNA aliases
            mirna_aliases = get_mirna_aliases(mirna)
            data = MirnaXGene.objects.filter(
                mirna__mirna_code__in=mirna_aliases, gene__in=gene_aliases)

        return data.filter(score__gte=score) if score else data


class MirnaAliasesList(generics.ListAPIView):
    """mirna-aliases endpoint"""
    serializer_class = MirnaAliasesSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering = ['mature_mirna']
    filterset_fields = ['mature_mirna', 'mirbase_accession_id']

    def get_queryset(self):
        return MirbaseIdMirna.objects.all()

    @extend_schema(
        tags=["miRNA"],
        summary="Lists miRNA Accession and mature IDs from miRBase.",
        parameters=[
            OpenApiParameter(name='mature_mirna', type=str,
                             description='Use to show only a specific miRNAs matures ID.',
                             examples=[
                                 OpenApiExample(name="", value=""),
                                 OpenApiExample(name="hsa-miR-21-5p", value="hsa-miR-21-5p"),
                                 OpenApiExample(name="hsa-miR-155-5p", value="hsa-miR-155-5p")
                             ]),
            OpenApiParameter(name='mirbase_accession_id', type=str,
                             description='Use to show only a specific miRNAs Accession ID.',
                             examples=[
                                 OpenApiExample(name="", value=""),
                                 OpenApiExample(name="MIMAT0000062", value="MIMAT0000062"),
                                 OpenApiExample(name="MIMAT0000063", value="MIMAT0000063")
                            ]),
            # Exclude pagination and ordering parameters
            OpenApiParameter(name='ordering', exclude=True),
            OpenApiParameter(name='page', exclude=True),
            OpenApiParameter(name='page_size', exclude=True)
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Returns all associations between miRNAs Accessions IDs (MIMAT) and miRNAs matures IDs from the miRBase database.
        """
        return super().get(request, *args, **kwargs)


class MirnaCodes(APIView):
    """
    Service that searches a list of miRNA codes and returns the code for the miRbase DB.
    """
    serializer_class = None

    @staticmethod
    def __get_mirna_code(mirna_code: str) -> str | None:
        """
        Receives a miRNA Previous ID or Accession ID, and returns the associated Accession ID.
        :param mirna_code: miRNA Previous ID or Accession ID.
        :return: The associated Accession ID.
        """
        res = MirbaseIdMirna.objects.filter(
            Q(mirbase_accession_id=mirna_code) | Q(mature_mirna=mirna_code)).first()
        if res:
            return res.mirbase_accession_id
        else:
            return None

    @extend_schema(
        tags=["miRNA"],
        summary="Retrieve miRNA codes",
        request={
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'mirna_codes': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'List of miRNA Previous IDs or Accession IDs to retrieve the associated Accession IDs.'
                        }
                    },
                    'required': ['mirna_codes']
                },
                'example': {'mirna_codes': ["name_01", "hsa-miR-487a-3p", "MIMAT0000066", "MI0026417", "hsa-let-7e-5p"]}
            }
        }
    )
    def post(self, request):
        data = request.data
        if "mirna_codes" not in data:
            return Response({"detail": "'mirna_codes' is mandatory"}, status=status.HTTP_400_BAD_REQUEST)

        mirna_codes = data["mirna_codes"]
        if not isinstance(mirna_codes, list):
            return Response({"detail": "'mirna_codes' must be of list type"}, status=status.HTTP_400_BAD_REQUEST)

        res = {}
        for mirna_id in mirna_codes:
            res[mirna_id] = self.__get_mirna_code(mirna_id)

        return Response(res)


class MirnaCodesFinder(APIView):
    """
    Service that takes a string of any length and returns a list of miRNA ids that contain that search criteria.
    """
    serializer_class = None

    @extend_schema(
        tags=["miRNA"],
        summary="Searches and lists miRNAs matching a string.",
        parameters=[
            OpenApiParameter(name='query', type=str,
                             description='miRNA search string.',
                             examples=[
                                 OpenApiExample(name="", value=""),
                                 OpenApiExample(name="hsa-miR-2", value="hsa-miR-2"),
                                 OpenApiExample(name="hsa-miR-1", value="hsa-miR-1")
                             ]
                            ),
            OpenApiParameter(name='limit', type=int,
                             description='number of elements returned by the service. 50 by default and a maximum of 3000.',
                             required=False
                        )
        ]
    )
    def get(self, _request):
        query = self.request.GET.get('query')
        if query is None:
            return Response([])

        res = []
        limit = self.request.GET.get('limit')
        limit = get_limit_parameter(limit)

        res_mirna = Mirna.objects.filter(mirna_code__istartswith=query)[
                    :limit].values_list('mirna_code', flat=True)
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
    """This functionality allows obtaining different information about a miRNA, such as its sequence, its previous identifiers and databases where information about it can be found."""
    serializer_class = MirnaSerializer
    pagination_class = None

    @extend_schema(
        tags=["miRNA"],
        summary="Retrieves miRNA details, including sequence, identifiers, and related databases.",
        parameters=[
            OpenApiParameter(name='mirna', type=str,
                             description='miRNA identifier (miRNA code or Accession ID).',
                             required=False,
                             examples=[
                                 OpenApiExample(name="", value=""),
                                 OpenApiExample(name="hsa-miR-548ai", value="hsa-miR-548ai"),
                                 OpenApiExample(name="hsa-miR-21-5p", value="hsa-miR-21-5p")
                             ])
            ]
        )
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
    """This service provides information, with evidence supported by experiments, on the relationships between miRNAs and human diseases."""
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

    @extend_schema(
        tags=["miRNA"],
        summary="Relationship between miRNAs and human diseases",
        parameters=[
            OpenApiParameter(name='mirna', type=str, 
                             description='miRNA (miRNA code or Accession ID) to get its interactions with different targets. If it is not specified, the service returns all the elements in a paginated response.',
                             required=False, 
                             examples=[
                                 OpenApiExample(name="", value=""),
                                 OpenApiExample(name="hsa-miR-891a-5p", value="hsa-miR-891a-5p"),
                                 OpenApiExample(name="hsa-miR-21-5p", value="hsa-miR-21-5p")
                             ]),
            OpenApiParameter(name='search', type=str,
                             description='Search by disease name',
                             required=False,
                             examples=[
                                    OpenApiExample(name="", value=""),
                                    OpenApiExample(name="Breast Neoplasms", value="Breast Neoplasms"),
                                    OpenApiExample(name="Atherosclerosis", value="Atherosclerosis")                             ]),
            # Exclude pagination and ordering parameters
            OpenApiParameter(name='ordering', exclude=True),
            OpenApiParameter(name='page', exclude=True),
            OpenApiParameter(name='page_size', exclude=True)
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        This service provides information, with evidence supported by experiments, on the relationships between miRNAs and human diseases.
        """
        return super().get(request, *args, **kwargs)


class MirnaDrugsList(generics.ListAPIView):
    """Drugs endpoint"""
    serializer_class = MirnaDrugsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter,
                       filters.SearchFilter, DjangoFilterBackend]
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

    @extend_schema(
        tags=["miRNA"],
        summary="Provides a list of drugs affecting miRNA expression.",
        parameters=[
            OpenApiParameter(name='mirna', type=str,
                             description='miRNA (miRNA code or Accession ID) to get its interactions with different targets. If it is not specified, the service returns all the elements in a paginated response.',
                             required=False,
                             examples=[
                                 OpenApiExample(name="", value=""),
                                 OpenApiExample(name="miR-126*", value="miR-126*"),
                                 OpenApiExample(name="miR-21", value="miR-21"),
                                 OpenApiExample(name="miR-155", value="miR-155")                             ]),
            OpenApiParameter(name='fda_approved', type=bool,
                             description='Defines if the drug is approved by the FDA'),
            OpenApiParameter(name='search', type=str,
                             description='Search by condition, small_molecule, and expression_pattern',
                             required=False,
                             examples=[
                                    OpenApiExample(name="", value=""),
                                    OpenApiExample(name="Arsenite", value="Arsenite"),
                                    OpenApiExample(name="up-regulated", value="up-regulated")                             ]),
            # Exclude pagination and ordering parameters
            OpenApiParameter(name='ordering', exclude=True),
            OpenApiParameter(name='page', exclude=True),
            OpenApiParameter(name='page_size', exclude=True)
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Returns a paginated response of experimentally validated small molecules (or drugs) that affect miRNA expression.
        """
        return super().get(request, *args, **kwargs)


class SubscribeUserToPubmed(APIView):
    @staticmethod
    @extend_schema(exclude=True)
    def get(request):
        email = request.GET.get("email")
        mirna = request.GET.get("mirna")
        gene = request.GET.get("gene")
        token = subscription_service.subscribe_user(
            email=email, mirna=mirna, gene=gene)
        return Response({'token': token}, status=status.HTTP_200_OK)


class UnsubscribeUserToPubmed(APIView):
    @staticmethod
    @extend_schema(exclude=True)
    def get(request):
        token = request.GET.get("token")
        subscription_service.unsubscribe_user(token=token)
        return Response("Your subscription has been deleted", status=status.HTTP_200_OK)


class MethylationSites(APIView):
    """
    Service that searches a list of methylation site identifiers from different Illumina array versions and
    returns the identifiers for the most recent version of the array.
    """

    serializer_class = None

    @staticmethod
    @extend_schema(
        tags=["Methylation"],
        summary="Retrieve Methylation sites",
        request={
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'methylation_sites': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'List of Methylation names.'
                        }
                    },
                    'required': ['methylation_sites']
                },
                'example': {"methylation_sites": ["cg17771854_BC11", "cg01615704_TC11"]}
            }
        }
    )
    def post(request):
        data = request.data
        if "methylation_sites" not in data:
            return Response({"detail": "'methylation_sites' is mandatory"}, status=status.HTTP_400_BAD_REQUEST)

        methylation_sites = data["methylation_sites"]
        if not isinstance(methylation_sites, list):
            return Response({"detail": "'methylation_sites' must be of list type"}, status=status.HTTP_400_BAD_REQUEST)

        # Generates a dict with the methylation sites as keys and the result of the query as values.
        res = {
            methylation_name: get_methylation_epic_sites_names(methylation_name)[1]
            for methylation_name in methylation_sites
        }

        return Response(res)


class MethylationSitesFinder(APIView):
    """
    Service that takes a text string of any length and returns a list of methylation site names (loci) containing
    that search criteria within the Illumina 'Infinium MethylationEPIC' array.
    """
    serializer_class = None

    @extend_schema(
        tags=["Methylation"],
        summary="Searches and lists Methylation sites matching a string.",
        parameters=[
            OpenApiParameter(name='query', type=str, 
                             description='Methylation search string.',
                             examples=[
                                 OpenApiExample(name="", value=""),
                                 OpenApiExample(name="cg25", value="cg25"),
                                 OpenApiExample(name="cg01", value="cg01")
                             ]
                             ),
            OpenApiParameter(name='limit', type=int,
                             description='number of elements returned by the service. 50 by default and a maximum of 3000.',
                             required=False
                             )
                        ]
    )
    def get(self, _request):
        query = self.request.GET.get('query')
        if query is None:
            return Response([])

        limit = self.request.GET.get('limit')
        limit = get_limit_parameter(limit)

        res = MethylationEPIC.objects.filter(name__istartswith=query)[
              :limit].values_list('name', flat=True)
        return Response(list(res))


class MethylationSitesToGenes(APIView):
    """A service that searches a list of CpG methylation site identifiers from different
    versions of Illumina arrays and returns the gene(s) they belong to."""

    serializer_class = None

    @staticmethod
    def __get_methylation_epic_sites_ids(input_name: str) -> list[str]:
        """
        Gets methylation sites from any type of Loci id
        :param input_name: String to query in the DB (site name)
        :return: list of ID of Methylation sites from EPIC v2 database
        """
        condition = get_methylation_match_condition(input_name)
        res = MethylationEPIC.objects.filter(condition).values_list('id', flat=True)
        return list(res)

    @staticmethod
    def __get_genes_from_methylation_epic_site(input_id: str) -> list[str]:
        """
        Gets genes from a specific methylation CpG site
        :param input_id: String to query in the DB (CpG ID)
        :return: Gene for the given input
        """
        gene = MethylationUCSCRefGene.objects.filter(
            Q(methylation_epic_v2_ilmnid=input_id)).values_list('ucsc_refgene_name', flat=True)
        return list(gene)

    @extend_schema(
        tags=["Methylation"],
        summary="Retrieve genes from methylation sites",
        request={
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'methylation_sites': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'list of Illumina array methylation site names or identifiers for which you want to know the gene(s).'
                        }
                    },
                    'required': ['methylation_sites']
                },
                'example': {"methylation_sites": ["cg17771854_BC11", "cg22461615_TC11", "name_007"]}
            }
        }
    )
    def post(self, request):
        data = request.data
        if "methylation_sites" not in data:
            return Response({"detail": "'methylation_sites' is mandatory"}, status=status.HTTP_400_BAD_REQUEST)

        methylation_sites = data["methylation_sites"]
        if not isinstance(methylation_sites, list):
            return Response({"detail": "'methylation_sites' must be of list type"}, status=status.HTTP_400_BAD_REQUEST)

        res = {}
        for methylation_name in methylation_sites:
            res[methylation_name] = []
            # For each CpG methylation site passed as a parameter... I look for its Identifier in the version of
            # the EPIC v2 array:
            epics_ids = self.__get_methylation_epic_sites_ids(methylation_name)
            for site_id in epics_ids:
                # For each identifier in the EPIC v2 array, I search for the genes involved:
                genes_list = self.__get_genes_from_methylation_epic_site(
                    site_id)

                [res[methylation_name].append(
                    gen) for gen in genes_list if gen not in res[methylation_name]]

            if len(res[methylation_name]) == 0:
                del res[methylation_name]

        return Response(res)


class MethylationDetails(APIView):
    """
    Service that obtains information about a specific CpG methylation site from
    the 'Infinium MethylationEPIC V2.0' array.
    """
    serializer_class = None

    @extend_schema(
        tags=["Methylation"],
        summary="Retrieve methylation details",
        parameters=[
            OpenApiParameter(
                name="methylation_site",
                description="Methylation site name from Illumina Infinium MethylationEPIC 2.0 array",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(name="cg22461615", value="cg22461615"),
                    OpenApiExample(name="cg00000029", value="cg00000029")
                ],
            )
        ]
    )
    def get(self, _request):
        methylation_site = self.request.GET.get('methylation_site')
        if not methylation_site:
            return Response(status=400, data={"'methylation_site' is mandatory"})

        res = {}
        # search for id in array
        epic_data = MethylationEPIC.objects.filter(
            Q(name=methylation_site)).first()

        if epic_data:
            # Loads name to response
            res["name"] = epic_data.name

            # Loads chromosome data
            if epic_data.strand_fr == "F":
                res["chromosome_position"] = epic_data.chr + \
                                             ":" + str(epic_data.mapinfo) + " [+]"
            elif epic_data.strand_fr == "R":
                res["chromosome_position"] = epic_data.chr + \
                                             ":" + str(epic_data.mapinfo) + " [-]"

            # load aliases to response
            res["aliases"] = []
            if epic_data.methyl27_loci and epic_data.methyl27_loci != epic_data.name:
                res["aliases"].append(epic_data.methyl27_loci)
            if epic_data.methyl450_loci and epic_data.methyl450_loci != epic_data.name:
                res["aliases"].append(epic_data.methyl450_loci)
            if epic_data.epicv1_loci and epic_data.epicv1_loci != epic_data.name:
                res["aliases"].append(epic_data.epicv1_loci)
            if epic_data.ilmnid and epic_data.ilmnid != epic_data.name:
                res["aliases"].append(epic_data.ilmnid)

            # searches and loads for islands relations
            islands_data = MethylationUCSC_CPGIsland.objects.filter(
                Q(methylation_epic_v2_ilmnid=epic_data.id))
            res["ucsc_cpg_islands"] = []
            for island in islands_data:
                res["ucsc_cpg_islands"].append(
                    {"cpg_island": island.ucsc_cpg_island_name, "relation": island.relation_to_ucsc_cpg_island})

            # searches and loads for genes relations
            genes_data = MethylationUCSCRefGene.objects.filter(
                Q(methylation_epic_v2_ilmnid=epic_data.id))
            res["genes"] = {}
            for gene in genes_data:
                if gene.ucsc_refgene_name not in res["genes"]:
                    res["genes"][gene.ucsc_refgene_name] = []
                if gene.ucsc_refgene_group not in res["genes"][gene.ucsc_refgene_name]:
                    res["genes"][gene.ucsc_refgene_name].append(
                        gene.ucsc_refgene_group)

            return Response(res)
        else:
            return Response(status=400, data={methylation_site + " is not a valid methylation site"})


def index(request: HttpRequest):
    """Returns the index.html page."""
    return render(request, 'index.html', {'version': settings.VERSION})
