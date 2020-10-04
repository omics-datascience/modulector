import logging
import os
import pathlib

import pandas as pd
from django.db import transaction

from modulector.models import MirnaDisease

logger = logging.getLogger(__name__)


def process():
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    file_path = os.path.join(parent_dir, "files/disease.txt")
    delimiter = "\t"
    logger.info("loading disease info")
    # loading files
    data = pd.read_csv(filepath_or_buffer=file_path,
                       delimiter=delimiter, encoding="ISO-8859-1")
    table_name = MirnaDisease._meta.db_table
    entities = []
    with transaction.atomic():
        logger.info("inserting data")
        for index, row in data.iterrows():
            category, mirna, disease, pmid, description = row

            # correcting fields because the send quotes sometimes
            disease = disease.replace("\"", "")
            description = description.replace("\"", "")
            mirna_disease = MirnaDisease(category=category, mirna=mirna,
                                         disease=disease, pmid=pmid, description=description)
            entities.append(mirna_disease)
        MirnaDisease.objects.bulk_create(entities)
        logger.info("data inserted")
