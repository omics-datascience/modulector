from rest_framework import serializers

from modulector.models import MirnaXGene, MirnaSource, Mirna, MirnaColumns, MirbaseIdMirna, MirnaDisease, MirnaDrugs, \
    Pubmed
from modulector.services import url_service


class MirnaColumnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirnaColumns
        fields = ['id', 'position', 'column_name', 'field_to_map', 'mirna_source_id']


class MirnaSourceSerializer(serializers.ModelSerializer):
    columns = MirnaColumnsSerializer(many=True)

    class Meta:
        model = MirnaSource
        fields = ['id', 'name', 'site_url', 'min_score', 'max_score', 'score_interpretation', 'description',
                  'synchronization_date', 'file_separator', 'columns']

    def create(self, validated_data):
        columns = validated_data.pop('columns')
        source = MirnaSource.objects.create(**validated_data)
        column_serializer = MirnaColumnsSerializer(many=True)
        for column in columns:
            column['mirna_source_id'] = source.id
        self.columns = column_serializer.create(columns)
        for column in self.columnsCharField:
            source.mirnacolumns.add(column)
        return source


class PubmedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pubmed
        fields = ['pubmed_id', 'pubmed_url']


class MirnaXGenSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(read_only=True, source='mirna_source.name')
    mirna = serializers.CharField(read_only=True, source='mirna.mirna_code')
    pubmed = PubmedSerializer(read_only=True, many=True)

    class Meta:
        model = MirnaXGene
        fields = ['id', 'mirna', 'gene', 'score', 'source_name', 'pubmed']


class MirnaSourceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirnaSource
        fields = ['id', 'name', 'site_url', 'min_score', 'max_score', 'score_interpretation', 'description',
                  'synchronization_date', 'file_separator', 'mirnacolumns']
        depth = 1


class MirbaseMatureMirnaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirbaseIdMirna
        fields = ['mirbase_accession_id', 'mature_mirna']


class MirnaSerializer(serializers.ModelSerializer):
    mirbase_accession_id = serializers.CharField(read_only=True, source='mirbase_accession_id.mirbase_accession_id')
    links = serializers.SerializerMethodField()

    class Meta:
        model = Mirna
        fields = ['mirna_code', 'mirna_sequence', 'mirbase_accession_id', 'links']

    def get_links(self, mirna):
        return url_service.build_urls(mirna_id=mirna.mirna_code)


class MirnaDiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirnaDisease
        fields = ['id', 'category', 'disease', 'pubmed_id', 'description']


class MirnaDrugsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirnaDrugs
        fields = ['id', 'small_molecule', 'fda_approved',
                  'detection_method', 'condition',
                  'pubmed_id', 'reference', 'expression_pattern', 'support']
