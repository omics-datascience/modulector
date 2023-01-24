import re
from typing import List

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
from modulector.services import processor_service, subscription_service
from modulector.services.processor_service import validate_processing_parameters

regex = re.compile(r'-\d[a-z]')


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
        mirna = self.request.query_params.get("mirna")
        gene = self.request.query_params.get("gene")
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
        mirna = self.request.query_params.get("mirna")
        if not mirna:
            raise ParseError(detail="mirna is obligatory")
        else:
            mirna = get_mirna_aliases(mirna)
            return MirnaXGene.objects.filter(mirna__mirna_code__in=mirna)


class Process(APIView):
    @staticmethod
    def get(request):
        commands = validate_processing_parameters(request)
        processor_service.execute(commands)
        return Response("data processed", status=status.HTTP_200_OK)


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
    """Service that takes a string of any length and returns a list of mirnas ids that contain that search criteria."""

    def get(self, request, format=None):
        limit = self.request.query_params.get('limit')
        query = self.request.query_params.get('query')
        if limit is None:
            limit = 50
        elif limit.isnumeric():
            limit = int(limit)
        else:
            return Response("'limit' parameter must be a numeric value", status=status.HTTP_400_BAD_REQUEST)
        if query is None:
            return Response([])

        res = Mirna.objects.filter(mirna_code__istartswith=query)[:limit].values_list('mirna_code', flat=True)
        return Response(list(res))


class MirnaList(viewsets.ReadOnlyModelViewSet):
    """Returns a single instance of miRNA with general data (mirna endpoint)"""
    serializer_class = MirnaSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        mirna = self.request.query_params.get("mirna")
        if not mirna:
            raise Http404
        aliases = get_mirna_aliases(mirna)
        instance = generics.get_object_or_404(Mirna, mirna_code__in=aliases)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        mirna = self.request.query_params.get("mirna")
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
        mirna = self.request.query_params.get("mirna")
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
        mirna = self.request.query_params.get("mirna")
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
        email = request.query_params.get("email")
        mirna = request.query_params.get("mirna")
        gene = request.query_params.get("gene")
        token = subscription_service.subscribe_user(email=email, mirna=mirna, gene=gene)
        return Response({'token': token}, status=status.HTTP_200_OK)


class UnsubscribeUserToPubmed(APIView):
    @staticmethod
    def get(request):
        token = request.query_params.get("token")
        subscription_service.unsubscribe_user(token=token)
        return Response("Your subscription has been deleted", status=status.HTTP_200_OK)


class MethylFinder(APIView):
    """Service that takes a text string of any length and returns a list of methylation site names (loci) containing
    that search criteria within the Illumina 'Infinium MethylationEPIC' array."""

    def get(self, request, format=None):
        limit = self.request.query_params.get('limit')
        query = self.request.query_params.get('query')
        if limit is None:
            limit = 50
        elif limit.isnumeric():
            limit = int(limit)
        else:
            return Response("'limit' parameter must be a numeric value", status=status.HTTP_400_BAD_REQUEST)
        if query is None:
            return Response([])

        res = MethylationEPIC.objects.filter(name__istartswith=query)[:limit].values_list('name', flat=True)
        return Response(list(res))

def index(request):
    return render(request, 'index.html', {'version': settings.VERSION})
