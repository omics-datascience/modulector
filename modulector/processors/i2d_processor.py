import logging
import os
import pathlib
import sys
from typing import List

import pandas as pandas
from django.db import connection, transaction
from django.utils.timezone import make_aware

from modulector.mappers import pubmed_mapper
from modulector.models import MirnaSource, MirnaXGene, Mirna

# TODO: remove fixed data.

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

parent_dir = pathlib.Path(__file__).parent.absolute().parent


def process(mirna_source: MirnaSource):
    """
    This functions process the data from I2D and loads the
    mirna gene table
    """
    ## Do to the size of this file, you should download it from the release files section. It is not in the repo.
    file_path = os.path.join(parent_dir, "files/i2d_database.txt")
    logger.info("loading data for i2d")
    # loading files
    series_names = mirna_source.mirnacolumns.order_by('position').values_list('field_to_map', flat=True)
    columns_to_use = mirna_source.mirnacolumns.order_by('position').values_list('position', flat=True)
    series_names = list(series_names)

    data_chunks = pandas.read_csv(filepath_or_buffer=file_path,
                                  delimiter=mirna_source.file_separator, header=None,
                                  names=series_names, usecols=columns_to_use, chunksize=10000000)
    logger.info("finding pubmeds")
    pubmed_dict = pubmed_mapper.execute()
    MirnaXGene.objects.filter(mirna_source=mirna_source).delete()
    for chunk in data_chunks:
        logger.info("grouping data")
        filtered_data = chunk[chunk["MIRNA"].str.contains("hsa")]
        grouped: pandas.DataFrame = filtered_data.groupby('MIRNA').aggregate(lambda tdf: tdf.unique().tolist())
        # insertion templates
        table_name = MirnaXGene._meta.db_table  # Obtenemos de manera dinamica el nombre de la tabla
        insert_query_prefix = f'INSERT INTO {table_name} (gene, score, mirna_source_id, mirna_id, pubmed_id, pubmed_url) VALUES '

        with transaction.atomic():
            logger.info("inserting chunk")
            for mirna_code, genes_and_scores in grouped.iterrows():
                mirna_obj = get_or_create_mirna(mirna_code)

                mirna_id: int = mirna_obj.pk
                insert_statements: List[str] = []

                # Generating tuples for insertion
                insert_template = "('{}',{}," + str(mirna_source.id) + "," + str(mirna_id) + ", {}, '{}')"
                for gene, score in zip(genes_and_scores['GENE'], genes_and_scores['SCORE']):
                    pubmed = 'null'
                    pubmed_url = 'null'
                    if mirna_code in pubmed_dict.keys():
                        pubmed = pubmed_dict[mirna_code]
                        pubmed_url = pubmed_mapper.build_url(pubmed)
                    insert_statements.append(insert_template.format(gene, score, pubmed, pubmed_url))

                # Grouping and inserting data
                insert_query = insert_query_prefix + ','.join(insert_statements)
                if insert_query_prefix == insert_query:
                    continue
                with connection.cursor() as cursor:
                    cursor.execute(insert_query)
    logger.info("insertion finished - synchronizing source")
    mirna_source.synchronization_date = make_aware(mirna_source.synchronization_date.now())
    mirna_source.save()


def get_or_create_mirna(mirna_code):
    """
    This method receives a mirna code and created the mirna if necessary
    Otherwise will return the object from the database
    """
    mirna_in_db = Mirna.objects.filter(mirna_code=mirna_code)
    if not mirna_in_db.exists():
        mirna_obj = Mirna(mirna_code=mirna_code)
        mirna_obj.save()
    else:
        mirna_obj = mirna_in_db.get()
    return mirna_obj
