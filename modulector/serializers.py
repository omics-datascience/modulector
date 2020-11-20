from rest_framework import serializers
from modulector.models import MirnaXGene, MirnaSource, Mirna, MirnaColumns, MirbaseIdMirna, MirnaDisease, MirnaDrugs


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
        for column in self.columns:
            source.mirnacolumns.add(column)
        return source


class MirnaXGenSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(read_only=True, source='mirna_source.name')
    mirna = serializers.CharField(read_only=True, source='mirna.mirna_code')

    class Meta:
        model = MirnaXGene
        fields = ['id', 'mirna', 'gene', 'score', 'pubmed_id', 'pubmed_url', 'source_name']


class MirnaSourceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirnaSource
        fields = ['id', 'name', 'site_url', 'min_score', 'max_score', 'score_interpretation', 'description',
                  'synchronization_date', 'file_separator', 'mirnacolumns']
        depth = 1


class MirnaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mirna
        fields = ['mirna_code']


class MirbaseMatureMirnaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirbaseIdMirna
        fields = ['mirbase_id', 'mature_mirna']


class MirnaDiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirnaDisease
        fields = ['id', 'category', 'mirna', 'disease', 'pubmed_id', 'description']


class MirnaDrugsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirnaDrugs
        fields = ['id', 'mature_mirna', 'mirbase_id', 'small_molecule', 'fda_approved', 'detection_method', 'condition',
                  'pubmed_id', 'reference', 'expression_pattern', 'support']
