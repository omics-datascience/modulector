import logging
import os
import pathlib
import sys

import pandas as pd
from django.db import transaction, connection

from modulector.models import GeneAliases

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


def process():
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    file_path = os.path.join(parent_dir, "files/gene_aliases.csv")
    delimiter = ","
    logger.info("loading gene_aliases info")
    # loading files
    data = pd.read_csv(filepath_or_buffer=file_path, names=['current', 'old', 'other'],
                       delimiter=delimiter, encoding="ISO-8859-1", header=None, skiprows=1)
    data = data[(data["old"].notnull() | data["other"].notnull())]
    entities_to_insert = []
    with transaction.atomic():
        logger.info("inserting data")
        for index, row in data.iterrows():
            gene_symbol, old, new = row
            # fix for specific case due to file interpretation, index 24222
            if pd.isna(gene_symbol) and old == 'NAC' and pd.isna(new):
                gene_symbol = 'NA'
            gene_symbol = gene_symbol.strip()
            aliases = []
            if old and not pd.isna(old):
                aliases.extend(old.split(","))
            if new and not pd.isna(new):
                aliases.extend(new.split(","))
            for alias in aliases:
                entities_to_insert.append(GeneAliases(gene_symbol=gene_symbol, alias=alias.strip()))
        with connection.cursor() as cursor:
            cursor.execute("truncate table modulector_gene_aliases")
        GeneAliases.objects.bulk_create(entities_to_insert)
        logger.info("data inserted")
