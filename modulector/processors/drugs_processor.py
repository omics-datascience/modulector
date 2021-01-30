import logging
import os
import pathlib
import sys

import pandas as pd
from django.db import transaction, connection

from modulector.models import MirnaDrugs

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


def process():
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    file_path = os.path.join(parent_dir, "files/drugs.xls")
    logger.info("loading drugs info")
    # loading files
    data = pd.read_excel(file_path)
    data = data[data["Species"].str.contains("Homo sapiens")]
    data = data.drop(['DB', 'CID', 'Species', 'Year'], axis=1)
    entities = []
    with transaction.atomic():
        logger.info("inserting data")
        for index, row in data.iterrows():
            mature_mirna, mirbase_accession_id, small_molecule, fda, detection_method, condition, pmid, \
            reference, suppport, expression_pattern = row

            mature_mirna = 'hsa-' + mature_mirna.lower()
            fda = (fda == 'approved')
            if pd.isna(mirbase_accession_id):
                mirbase_accession_id = ''

            mirna_drug = MirnaDrugs(mature_mirna=mature_mirna, mirbase_accession_id=mirbase_accession_id, small_molecule=small_molecule,
                                    fda_approved=fda, detection_method=detection_method, condition=condition,
                                    pubmed_id=pmid,
                                    reference=reference, support=suppport, expression_pattern=expression_pattern)
            entities.append(mirna_drug)
        with connection.cursor() as cursor:
            cursor.execute("truncate table modulector_mirnadrugs")
        MirnaDrugs.objects.bulk_create(entities)
        logger.info("data inserted")
