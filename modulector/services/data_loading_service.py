import logging
import os
import sys

from modulector.mappers.gene_mapper import GeneMapper
from modulector.mappers.mature_mirna_mapper import MatureMirnaMapper
from modulector.mappers.ref_seq_mapper import RefSeqMapper
from modulector.processors import disease_processor

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


def load_data():
    # this variable show be set when you before running the code
    should_load_data = os.environ['LOAD_DATA']
    if should_load_data == '1':
        logger.info("preloading required data")
        mirbase_mapper = MatureMirnaMapper()
        mirbase_mapper.execute()

        disease_processor.process()

        ref_seq_mapper = RefSeqMapper()
        ref_seq_mapper.execute()

        gene_mapper = GeneMapper()
        gene_mapper.execute()
