import logging
import os
import pathlib
from typing import List

import pandas as pandas
from django.db import connection, transaction
from django.utils.timezone import make_aware

from modulector.mappers.gene_mapper import GeneMapper
from modulector.mappers.mature_mirna_mapper import MatureMirnaMapper
from modulector.mappers.ref_seq_mapper import RefSeqMapper
from modulector.models import MirnaSource, MirnaXGene, Mirna, OldRefSeqMapping, GeneSymbolMapping
# TODO: add documentation to all the functions and remove fixed data.
from modulector.processors import disease_processor

logger = logging.getLogger(__name__)
parent_dir = pathlib.Path(__file__).parent.absolute().parent
file_map = dict()
file_map["large"] = os.path.join(parent_dir, "files/mirdb_data.txt")


def process(source_id: int):
    mirbase_mapper = MatureMirnaMapper()
    mirbase_mapper.execute()
    disease_processor.process()
    file_path = file_map["large"]
    logger.info("loading data")
    # loading files
    mirna_source = MirnaSource.objects.get(id=source_id)
    series_names = mirna_source.mirnacolumns.order_by('position').values_list('field_to_map', flat=True)
    series_names = list(series_names)

    data = pandas.read_csv(filepath_or_buffer=file_path,
                           delimiter=mirna_source.file_separator, header=None, names=series_names)

    logger.info("grouping data")
    filtered_data = data[data["MIRNA"].str.contains("hsa")]
    grouped: pandas.DataFrame = filtered_data.groupby('MIRNA').aggregate(lambda tdf: tdf.unique().tolist())
    ref_seq_mapper = RefSeqMapper()
    ref_seq_mapper.execute()
    ref_seq_list = list(OldRefSeqMapping.objects.all().values_list())
    ref_seq_map = dict()
    for index, old, new in ref_seq_list:
        ref_seq_map[old] = new
    gene_mapper = GeneMapper()
    gene_mapper.execute()
    symbol_list = list(GeneSymbolMapping.objects.all().values_list())
    symbol_map = dict()
    for index, refseq, symbol in symbol_list:
        symbol_map[refseq] = symbol

    logger.info("inserting data")
    # insertion templates
    table_name = MirnaXGene._meta.db_table  # Obtenemos de manera dinamica el nombre de la tabla
    insert_query_prefix = f'INSERT INTO {table_name} (gene, score, mirna_source_id, mirna_id) VALUES '

    with transaction.atomic():
        logger.info("inserting data")
        MirnaXGene.objects.filter(mirna_source=mirna_source).delete()
        for mirna_code, genes_and_scores in grouped.iterrows():
            mirna_obj = get_or_create_mirna(mirna_code)

            mirna_id: int = mirna_obj.pk
            insert_statements: List[str] = []

            # Generating tuples for insertion
            insert_template = "('{}',{}," + str(source_id) + "," + str(mirna_id) + ")"
            for gene, score in zip(genes_and_scores['GEN'], genes_and_scores['SCORE']):
                if gene in ref_seq_map:
                    gene = ref_seq_map[gene]
                if gene in symbol_map:
                    insert_statements.append(insert_template.format(symbol_map[gene], score))

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
    mirna_in_db = Mirna.objects.filter(mirna_code=mirna_code)
    if not mirna_in_db.exists():
        mirna_obj = Mirna(mirna_code=mirna_code)
        mirna_obj.save()
    else:
        mirna_obj = mirna_in_db.get()
    return mirna_obj
