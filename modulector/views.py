import re

from django.core.cache import caches
from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from modulector.models import MirnaXGene, MirnaSource, Mirna, MirnaColumns, MirbaseIdMirna, MirnaDisease
from modulector.serializers import MirnaXGenSerializer, MirnaSourceSerializer, MirnaSerializer, \
    MirnaSourceListSerializer, MirbaseMatureMirnaSerializer, MirnaDiseaseSerializer
# TODO: remove unused code
# TODO: use Generics when possible
# TODO: use '_' for unused params on the left of used params, remove the ones on the right
from modulector.services import url_service, processor_service

regex = re.compile(r'-\d{1}[a-z]{1}')


class MirnaXGenList(APIView):
    display_page_controls = True

    def get(self, request):
        cache = caches['default']
        gene = self.request.query_params.get("gene", None)
        mirna = self.request.query_params.get("mirna", None)
        if mirna is None and gene is None:
            return Response([], status=status.HTTP_200_OK)
        mirna_id = Mirna.objects.get(mirna_code=mirna).id
        if mirna is not None and gene is not None:
            key = str(mirna_id) + str(gene)
            result = cache.get(key)
            if result is None:
                result = MirnaXGene.objects.filter(mirna=mirna_id, gene=gene)
                cache.add(key, result)
            data = Response(MirnaXGenSerializer(result, many=True).data, status=status.HTTP_200_OK)
        else:
            key = str(mirna_id)
            result = cache.get(key)
            paginator = PageNumberPagination()
            if result is None:
                result = MirnaXGene.objects.filter(mirna=mirna_id)
                cache.add(key, result)
            result = paginator.paginate_queryset(result, self.request)
            serializer = MirnaXGenSerializer(result, many=True)
            data = paginator.get_paginated_response(serializer.data)
        return data


class MirnaSourcePostAndList(APIView):
    def post(self, request, *args, **kwargs):
        serializer = MirnaSourceSerializer(data=request.data)
        if serializer.is_valid():
            source = serializer.save()
            # TODO: remove all() as filter() is already a QuerySet
            source.columns = MirnaColumns.objects.filter(mirna_source_id=source.id).all()
            serializer = MirnaSourceSerializer(source)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessPost(APIView):
    def post(self, request, *args, **kwargs):
        processor_service.execute((request.data["source_id"]))
        return Response("data processed", status=status.HTTP_200_OK)


class MirnaSourceList(APIView):
    # TODO: implment with Generics.ListAPIView for simplicity
    def get(self, request):
        sources = MirnaSource.objects.all()
        serializer = MirnaSourceListSerializer(sources, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MirbaseMatureList(generics.ListAPIView):
    serializer_class = MirbaseMatureMirnaSerializer

    # TODO: refactor
    def get_queryset(self):
        mirna = self.request.query_params.get("mirna", None)
        result = MirbaseIdMirna.objects.all()
        if mirna is not None:
            result = result.filter(mature_mirna=mirna)
        return result


class MirnaList(generics.ListAPIView):
    serializer_class = MirnaSerializer

    # TODO: refactor
    def get_queryset(self):
        mirna = self.request.query_params.get("mirna", None)
        if mirna is None:
            result = Mirna.objects.all()
        else:
            result = Mirna.objects.filter(mirna_code=mirna)
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
        if mirna:
            mirna = mirna.lower()
            mirna = re.sub(regex, "", mirna)
            return MirnaDisease.objects.filter(mirna__startswith=mirna)
        return MirnaDisease.objects.all()
