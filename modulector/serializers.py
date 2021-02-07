from rest_framework import serializers

from modulector.models import MirnaXGene, MirnaSource, Mirna, MirnaColumns, MirbaseIdMirna, MirnaDisease, MirnaDrugs
from modulector.services import url_service
from modulector.utils import link_builder


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


class MirnaXGenSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(read_only=True, source='mirna_source.name')
    mirna = serializers.CharField(read_only=True, source='mirna.mirna_code')
    pubmeds = serializers.SerializerMethodField()

    class Meta:
        model = MirnaXGene
        fields = ['id', 'mirna', 'gene', 'score', 'source_name', 'pubmeds']

    def get_pubmeds(self, mirnaxgene):
        return [pubmed[2] for pubmed in mirnaxgene.pubmed.values_list()]


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
    aliases = serializers.SerializerMethodField()

    class Meta:
        model = Mirna
        fields = ['aliases', 'mirna_sequence', 'mirbase_accession_id', 'links']

    def get_links(self, mirna):
        return url_service.build_urls(mirna_id=mirna.mirna_code)

    def get_aliases(self, mirna):
        return get_mirna_aliases(mirna.mirna_code)


class MirnaDiseaseSerializer(serializers.ModelSerializer):
    pubmed = serializers.SerializerMethodField()

    class Meta:
        model = MirnaDisease
        fields = ['id', 'category', 'disease', 'pubmed', 'description']

    def get_pubmed(self, disease):
        return link_builder.build_pubmed_url(disease.pubmed_id)


class MirnaDrugsSerializer(serializers.ModelSerializer):
    pubmed = serializers.SerializerMethodField()

    class Meta:
        model = MirnaDrugs
        fields = ['id', 'small_molecule', 'fda_approved',
                  'detection_method', 'condition',
                  'pubmed', 'reference', 'expression_pattern', 'support']

    def get_pubmed(self, drug):
        return link_builder.build_pubmed_url(drug.pubmed_id)


def get_mirna_aliases(code):
    # code can be mirna or mimat
    aliases = [code]
    if code.startswith('MI'):
        mirnas = get_mirna_from_accession(code)
        aliases.extend(mirnas)
    else:
        accession_id = get_accession_from_mirna(code)
        mirnas = get_mirna_from_accession(accession_id)
        aliases.append(accession_id)
        for mirna in mirnas:
            if mirna not in aliases:
                aliases.append(mirna)
    return aliases


def get_mirna_from_accession(accession_id):
    record = MirbaseIdMirna.objects.filter(mirbase_accession_id=accession_id)
    if record:
        mirnas = [record[2] for record in record.values_list()]
        return mirnas


def get_accession_from_mirna(mirna_code):
    record = MirbaseIdMirna.objects.filter(mature_mirna=mirna_code)
    if record:
        return record.get().mirbase_accession_id
