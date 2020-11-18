import re
from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from modulector.models import MirnaXGene, MirnaSource, Mirna, MirnaColumns, MirbaseIdMirna, MirnaDisease, MirnaDrugs
from modulector.pagination import StandardResultsSetPagination
from modulector.serializers import MirnaXGenSerializer, MirnaSourceSerializer, MirnaSerializer, \
    MirnaSourceListSerializer, MirbaseMatureMirnaSerializer, MirnaDiseaseSerializer, MirnaDrugsSerializer
from modulector.services import url_service, processor_service

regex = re.compile(r'-\d{1}[a-z]{1}')


class MirnaXGenList(generics.ListAPIView):
    serializer_class = MirnaXGenSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        gene = self.request.query_params.get("gene")
        mirna = self.request.query_params.get("mirna")
        if mirna is None and gene is None:
            return MirnaXGene.objects.none()

        query = MirnaXGene.objects.filter(mirna__mirna_code=mirna)
        if gene is not None:
            query = query.filter(gene=gene)

        return query


class MirnaSourcePostAndList(APIView):
    def post(self, request, *args, **kwargs):
        serializer = MirnaSourceSerializer(data=request.data)
        if serializer.is_valid():
            source = serializer.save()
            source.columns = MirnaColumns.objects.filter(mirna_source_id=source.id)
            serializer = MirnaSourceSerializer(source)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessPost(APIView):
    def post(self, request, *args, **kwargs):
        processor_service.execute((request.data["source_id"]))
        return Response("data processed", status=status.HTTP_200_OK)


class MirnaSourceList(generics.ListAPIView):
    serializer_class = MirnaSourceListSerializer

    def get_queryset(self):
        return MirnaSource.objects.all()


class MirbaseMatureList(generics.ListAPIView):
    serializer_class = MirbaseMatureMirnaSerializer

    def get_queryset(self):
        mirna = self.request.query_params.get("mirna", None)
        result = MirbaseIdMirna.objects.all()
        if mirna is not None:
            result = result.filter(mature_mirna=mirna)
        return result


class MirnaList(generics.ListAPIView):
    serializer_class = MirnaSerializer

    def get_queryset(self):
        mirna = self.request.query_params.get("mirna", None)
        result = Mirna.objects.all()
        if mirna:
            result = result.filter(mirna_code=mirna)
        return result


class LinksList(APIView):
    def get(self, request):
        mirna = self.request.query_params.get("mirna", None)
        links = url_service.build_urls(mirna)
        return Response(links, status=status.HTTP_200_OK)


class MirnaDiseaseList(generics.ListAPIView):
    serializer_class = MirnaDiseaseSerializer

    def get_queryset(self):
        mirna = self.request.query_params.get("mirna")
        result = MirnaDisease.objects.all()
        if mirna:
            mirna = mirna.lower()
            mirna = re.sub(regex, "", mirna)
            result = result.filter(mirna__startswith=mirna)
        return result


class MirnaDrugsList(generics.ListAPIView):
    serializer_class = MirnaDrugsSerializer

    def get_queryset(self):
        mirna = self.request.query_params.get("mirna")
        mirbase = self.request.query_params.get("mirbase")
        query_set = MirnaDrugs.objects.all()
        if mirna:
            query_set = query_set.filter(mature_mirna__endswith=mirna)
        if mirbase:
            query_set = query_set.filter(mirbase_id=mirbase)
        return query_set


def index(request):
    return render(request, 'index.html')
