import time

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from modulector.dataSourceProcessors import miRDBProcessor
from modulector.models import MirnaXGen, MirnaSource, Mirna, MirnaColumns
from modulector.serializers import MirnaXGenSerializer, MirnaSourceSerializer, MirnaSerializer, \
    MirnaSourceListSerializer


class MirnaXGenList(generics.ListAPIView):
    queryset = MirnaXGen.objects.all()
    serializer_class = MirnaXGenSerializer

    def get_queryset(self):
        return MirnaXGen.objects.all()


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
        return Mirna.objects.all()
