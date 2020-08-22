import time

from django.core.cache import caches
from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from modulector.dataSourceProcessors import miRDBProcessor
from modulector.models import MirnaXGen, MirnaSource, Mirna, MirnaColumns
from modulector.serializers import MirnaXGenSerializer, MirnaSourceSerializer, MirnaSerializer, \
    MirnaSourceListSerializer


class MirnaXGenList(APIView):
    display_page_controls = True

    def get(self, request):
        cache = caches['default']
        gen = self.request.query_params.get("gen", None)
        mirna = self.request.query_params.get("mirna", None)
        if mirna is None and gen is None:
            return None
        mirna_id = Mirna.objects.get(mirna_code=mirna).id
        data = []
        if mirna is not None and gen is not None:
            key = str(mirna_id) + str(gen)
            result = cache.get(key)
            if result is None:
                result = MirnaXGen.objects.filter(mirna=mirna_id, gen=gen)
                cache.add(key, result)
            data = Response(MirnaXGenSerializer(result, many=True).data, status=status.HTTP_200_OK)
        else:
            key = str(mirna_id)
            result = cache.get(key)
            paginator = PageNumberPagination()
            page = self.request.query_params.get('page')
            if result is None:
                result = MirnaXGen.objects.filter(mirna=mirna_id)
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
            source.columns = MirnaColumns.objects.filter(mirna_source_id=source.id).all()
            serializer = MirnaSourceSerializer(source)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessPost(APIView):
    def post(self, request, *args, **kwargs):
        start = time.time()
        print("ARRANcO" + str(start))
        miRDBProcessor.process(request.data["source_id"])
        end = time.time()
        print(end - start)
        print("termino")
        return Response("data processed", status=status.HTTP_200_OK)


class MirnaSourceList(APIView):
    def get(self, request):
        sources = MirnaSource.objects.all()
        serializer = MirnaSourceListSerializer(sources, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MirnaList(generics.ListAPIView):
    serializer_class = MirnaSerializer

    def get_queryset(self):
        mirna = self.request.query_params.get("mirna", None)
        if mirna is None:
            result = Mirna.objects.all()
        else:
            result = Mirna.objects.filter(mirna_code=mirna)
        return result
