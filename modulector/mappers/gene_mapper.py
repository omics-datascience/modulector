import os
import pathlib
from typing import List

import pandas as pd
from django.db import transaction, connection

parent_dir = pathlib.Path(__file__).parent.absolute().parent
path = os.path.join(parent_dir, "files/ref_seq_to_symbols.txt")


def process():
    translations = load_translations()
    with transaction.atomic():
        insert_query_prefix = f'INSERT INTO modulector_genesymbolmapping (refseq, symbol) VALUES '
        insert_template = "('{}','{}')"
        queries: List[str] = []
        for refseq in translations.keys():
            queries.append(insert_template.format(refseq, translations.get(refseq)))
        insert_query = insert_query_prefix + ','.join(queries)
        with connection.cursor() as cursor:
            cursor.execute("truncate table modulector_genesymbolmapping")
            cursor.execute(insert_query)


def load_translations():
    df = pd.read_csv(filepath_or_buffer=path, delimiter="\t")
    symbol_dic = {}
    for index, item in df.iterrows():
        ref_seq = item["RNA"].split(".")[0]
        symbol = item["Symbol"]
        symbol_dic[ref_seq] = symbol
    return symbol_dic
