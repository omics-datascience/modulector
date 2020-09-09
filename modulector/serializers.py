from rest_framework import serializers
from modulector.models import MirnaXGen, MirnaSource, Mirna, MirnaColumns


class MirnaColumnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirnaColumns
        fields = ['id', 'position', 'column_name', 'field_to_map', 'mirna_source_id']


class MirnaSourceSerializer(serializers.ModelSerializer):
    columns = MirnaColumnsSerializer(many=True)

    class Meta:
        model = MirnaSource
        fields = ['id', 'name', 'site_url', 'min_score', 'max_score', 'score_interpretation', 'description',
                  'synchronization_date', 'file_type', 'file_separator', 'columns']

    def create(self, validated_data):
        columns = validated_data.pop('columns')
        source = MirnaSource.objects.create(**validated_data)
        column_serializer = MirnaColumnsSerializer(many=True)
        for column in columns:
            column['mirna_source_id'] = source.id
        self.columns = column_serializer.create(columns)
        for column in self.columns:
            source.mirnacolumns.add(column)
        return source


class MirnaXGenSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True, source='mirna_source.name')
    mirna = serializers.CharField(read_only=True, source='mirna.mirna_code')

    class Meta:
        model = MirnaXGen
        fields = ['mirna', 'gen', 'score', 'pubmed_id', 'pubMedUrl', 'name']


class MirnaSourceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirnaSource
        fields = ['id', 'name', 'site_url', 'min_score', 'max_score', 'score_interpretation', 'description',
                  'synchronization_date', 'file_type', 'file_separator', 'mirnacolumns']
        depth = 1


class MirnaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mirna
        fields = ['mirna_code']
