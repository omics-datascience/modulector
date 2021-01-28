import logging
import os
import sys

from modulector.mappers import ref_seq_mapper, gene_mapper, mature_mirna_mapper
from modulector.processors import disease_processor, drugs_processor, sequence_processor

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


def load_data():
    # this variable show be set when you before running the code
    should_load_data = os.environ['LOAD_DATA']
    if should_load_data == '1':
        sequence_processor.process()
        logger.info("preloading required data")
        drugs_processor.process()
        mature_mirna_mapper.execute()
        disease_processor.process()
        ref_seq_mapper.execute()
        gene_mapper.execute()
        sequence_processor()
