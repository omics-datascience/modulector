import logging
from typing import List, Optional, Dict, Set
from rest_framework import serializers
from ModulectorBackend.settings import USE_PUBMED_API, PUBMED_API_TIMEOUT
from modulector.models import MirnaXGene, MirnaSource, Mirna, MirnaColumns, MirbaseIdMirna, MirnaDisease, MirnaDrug
from modulector.services import url_service, pubmed_service
from modulector.utils import link_builder


class MirnaColumnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirnaColumns
        fields = ['id', 'position', 'column_name',
                  'field_to_map', 'mirna_source_id']


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
    source_name = serializers.CharField(
        read_only=True, source='mirna_source.name')
    mirna = serializers.CharField(read_only=True, source='mirna.mirna_code')
    pubmeds = serializers.SerializerMethodField(method_name='get_pubmeds')
    sources = serializers.SerializerMethodField(method_name='get_sources')

    class Meta:
        model = MirnaXGene
        fields = ['id', 'mirna', 'gene', 'score',
                  'source_name', 'pubmeds', 'sources', 'score_class']
    
    def get_pubmeds(self, mirna_gene_interaction: MirnaXGene) -> Set[str]:
        """
        Gets a list of related Pubmed URLs to a miRNA-Gene interaction.
        :param mirna_gene_interaction: miRNA-Gene interaction.
        :return: List of Pubmed URLs.
        """
        pubmed_urls: Set[str] = set()

        if not self.context["include_pubmeds"]:
            return pubmed_urls

        pubmed_urls.update(
            list(mirna_gene_interaction.pubmed.values_list('pubmed_url', flat=True))
        )

        # If the api call is enabled, it will query the API and get the pubmeds
        mirna = mirna_gene_interaction.mirna.mirna_code
        gene = mirna_gene_interaction.gene
        term = pubmed_service.build_search_term(mirna, gene)
        if USE_PUBMED_API:  # Checks if the api call is enabled in the settings
            try:
                api_pubmeds = pubmed_service.query_parse_and_build_pumbeds(term=term, mirna=mirna,
                                                                           gene=gene, timeout=PUBMED_API_TIMEOUT)

                pubmed_urls.update([link_builder.build_pubmed_url(pubmed_id) for pubmed_id in api_pubmeds])
            except Exception as ex:
                # Only handles exceptions in this case
                logging.error('Error getting PubMeds:')
                logging.exception(ex)
                return set()

        return pubmed_urls

    @staticmethod
    def get_sources(mirna_gene_interaction: MirnaXGene) -> List[str]:
        """
        Gets a list of sources for a miRNA-Gene interaction
        :param mirna_gene_interaction: miRNA-Gene interaction
        :return: List of sources for the interaction
        """
        sources = mirna_gene_interaction.sources
        if sources:
            return sources.split('|')
        return []


class MirnaAliasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MirbaseIdMirna
        fields = ['mirbase_accession_id', 'mature_mirna']


class MirnaSerializer(serializers.ModelSerializer):
    mirbase_accession_id = serializers.CharField(
        read_only=True, source='mirbase_accession_id.mirbase_accession_id')
    links = serializers.SerializerMethodField(method_name='get_links')
    aliases = serializers.SerializerMethodField(method_name='get_aliases')

    class Meta:
        model = Mirna
        fields = ['aliases', 'mirna_sequence', 'mirbase_accession_id', 'links']

    @staticmethod
    def get_links(mirna: Mirna) -> List[Dict]:
        """
        Gets a list of sources links for a specific miRNA.
        :param mirna: miRNA object.
        :return: List of sources links.
        """
        mirbase_id_obj = mirna.mirbase_accession_id
        if mirbase_id_obj is not None:
            return url_service.build_urls(mirna_id=mirbase_id_obj.mirbase_accession_id)
        return []

    @staticmethod
    def get_aliases(mirna: Mirna) -> List[str]:
        """
        Gets a miRNA aliases.
        :param mirna: miRNA object to get its aliases.
        :return: List of miRNA aliases.
        """
        return get_mirna_aliases(mirna.mirna_code)


class MirnaDiseaseSerializer(serializers.ModelSerializer):
    pubmed = serializers.SerializerMethodField(method_name='get_pubmed')

    class Meta:
        model = MirnaDisease
        fields = ['id', 'category', 'disease', 'pubmed', 'description']

    @staticmethod
    def get_pubmed(disease: MirnaDisease) -> str:
        """
        Gets a PubMed URL for a miRNA-disease association.
        :param disease: MirnaDisease object.
        :return: Pubmed URL.
        """
        return link_builder.build_pubmed_url(disease.pubmed_id)


class MirnaDrugsSerializer(serializers.ModelSerializer):
    pubmed = serializers.SerializerMethodField(method_name='get_pubmed')

    class Meta:
        model = MirnaDrug
        fields = ['id', 'small_molecule', 'fda_approved',
                  'detection_method', 'condition',
                  'pubmed', 'reference', 'expression_pattern', 'support']

    @staticmethod
    def get_pubmed(drug: MirnaDrug) -> str:
        """
        Gets a Pubmed URL for a miRNA-drug association
        :param drug: MirnaDrugs object
        :return: Pubmed URL
        """
        return link_builder.build_pubmed_url(drug.pubmed_id)


def get_mirna_aliases(mirna_code: str) -> List[str]:
    """
    Gets all the aliases for a miRNA code (not duplicates)
    :param mirna_code: miRNA code to get its aliases
    :return: List of miRNA aliases
    """
    # miRNA code can be simple miRNA code or an accession id (MIMAT ID)
    if mirna_code.startswith('MI'):
        aliases = get_mirna_from_accession(mirna_code)
    else:
        accession_id = get_accession_from_mirna(mirna_code)
        if accession_id is not None:
            aliases = get_mirna_from_accession(accession_id)
            aliases.append(accession_id)
        else:
            aliases = []

    # Adds miRNA code to not omit it
    aliases.append(mirna_code)
    return aliases


def get_mirna_from_accession(accession_id: str) -> List[str]:
    """
    Retrieves from DB all the miRNA aliases (not duplicates) for a specific accession id.
    :param accession_id: Accession id to make the query
    :return: List of related miRNA aliases
    """
    return list(
        MirbaseIdMirna.objects.filter(
            mirbase_accession_id=accession_id
        ).values_list('mature_mirna', flat=True).distinct()
    )


def get_accession_from_mirna(mirna_code: str) -> Optional[str]:
    """
    Retrieves an accession id from a miRNA code.
    :param mirna_code: miRNA code to make the query
    :return: Accession id if found, None otherwise
    """
    record = MirbaseIdMirna.objects.filter(mature_mirna=mirna_code).first()
    return record.mirbase_accession_id if record is not None else None
