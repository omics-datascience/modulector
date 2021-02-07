import re

from django.http import Http404
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView

from modulector.models import MirnaXGene, MirnaSource, Mirna, MirnaColumns, MirbaseIdMirna, MirnaDisease, MirnaDrugs
from modulector.pagination import StandardResultsSetPagination
from modulector.serializers import MirnaXGenSerializer, MirnaSourceSerializer, MirnaSerializer, \
    MirnaSourceListSerializer, MirbaseMatureMirnaSerializer, MirnaDiseaseSerializer, MirnaDrugsSerializer, \
    get_mirna_from_accession, get_mirna_aliases
from modulector.services import processor_service

regex = re.compile(r'-\d[a-z]')


class MirnaXGenList(generics.ListAPIView):
    serializer_class = MirnaXGenSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    ordering_fields = ['gene', 'score', 'mirna_source.name']
    search_fields = ['gene']
    filterset_fields = ['gene']

    def get_queryset(self):
        mirna = self.request.query_params.get("mirna")
        if not mirna:
            return MirnaXGene.objects.none()
        else:
            mirna = get_mirna_aliases(mirna)
            return MirnaXGene.objects.filter(mirna__mirna_code__in=mirna)


class MirnaSourcePostAndList(APIView):
    @staticmethod
    def post(request):
        serializer = MirnaSourceSerializer(data=request.data)
        if serializer.is_valid():
            source = serializer.save()
            source.columns = MirnaColumns.objects.filter(mirna_source_id=source.id)
            serializer = MirnaSourceSerializer(source)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessPost(APIView):
    @staticmethod
    def post(request):
        processor_service.execute((request.data["source_id"]))
        return Response("data processed", status=status.HTTP_200_OK)


class MirnaSourceList(generics.ListAPIView):
    serializer_class = MirnaSourceListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return MirnaSource.objects.all()


class MirbaseMatureList(generics.ListAPIView):
    serializer_class = MirbaseMatureMirnaSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        mirna = self.request.query_params.get("mirna", None)
        result = MirbaseIdMirna.objects.all()
        if mirna is not None:
            result = result.filter(mature_mirna=mirna)
        return result


class MirnaList(generics.ListAPIView):
    serializer_class = MirnaSerializer
    pagination_class = None

    def get_queryset(self):
        mirna = self.request.query_params.get("mirna", None)
        if mirna:
            aliases = get_mirna_aliases(mirna)
            result = Mirna.objects.filter(mirna_code__in=aliases)
            return result
        else:
            raise Http404


class MirnaDiseaseList(generics.ListAPIView):
    serializer_class = MirnaDiseaseSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['disease']
    search_fields = ['disease']

    def get_queryset(self):
        mirna = self.request.query_params.get("mirna")
        result = MirnaDisease.objects.all()
        if mirna:
            if mirna.startswith('MI'):
                mirna = get_mirna_from_accession(mirna)
                result = result.filter(mirna__in=mirna)
            else:
                mirna = mirna.lower()
                if mirna.count('-') == 3:
                    mirna = re.sub(regex, "", mirna)
                result = result.filter(mirna__contains=mirna)
        return result


class MirnaDrugsList(generics.ListAPIView):
    serializer_class = MirnaDrugsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    ordering_fields = ['condition', 'detection_method', 'small_molecule', 'expression_pattern', 'reference',
                       'support']
    search_fields = ['condition', 'small_molecule', 'expression_pattern']
    filterset_fields = ['fda_approved']

    def get_queryset(self):
        mirna = self.request.query_params.get("mirna")
        query_set = MirnaDrugs.objects.all()
        if mirna:
            if mirna.startswith('MI'):
                mirna = get_mirna_from_accession(mirna)
                query_set = query_set.filter(mature_mirna__in=mirna)

            query_set = query_set.filter(mature_mirna__contains=mirna)
        return query_set


def index(request):
    return render(request, 'index.html')
