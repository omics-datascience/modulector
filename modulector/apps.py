from django.apps import AppConfig

from modulector.mappers.gene_mapper import GeneMapper
from modulector.mappers.ref_seq_mapper import RefSeqMapper


class ModulectorConfig(AppConfig):
    name = 'modulector'

    def ready(self):
        gene_mapper = GeneMapper()
        ref_seq_mapper = RefSeqMapper()
        gene_mapper.execute()
        ref_seq_mapper.execute()
