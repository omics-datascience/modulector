import os
import pathlib
from typing import List

import mygene as gene_api
import pandas as pd
from django.db import transaction, connection

parent_dir = pathlib.Path(__file__).parent.absolute().parent
path = os.path.join(parent_dir, "files/ref_seq_to_symbols.txt")


class GeneMapper:
    def execute(self, ref_seq_array, old_ref_seq_array):
        translations = load_translations()
        missing_translations = []
        for ref in ref_seq_array:
            if ref not in translations.keys() and ref not in old_ref_seq_array:
                missing_translations.append(ref)
        print("missing ref" + str(len(missing_translations)))
        data_to_append = ""
        translated_from_api = translate_ref_seq(missing_translations)
        for key in translated_from_api.keys():
            data_to_append += translated_from_api[key] + "\t" + key + "\n"
        with open(path, "a") as f:
            f.write(data_to_append)
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
    symbol_dic = dict()
    for index, item in df.iterrows():
        ref_seq = item["RNA"].split(".")[0]
        symbol = item["Symbol"]
        symbol_dic[ref_seq] = symbol
    return symbol_dic


def translate_ref_seq(missing_list):
    api = gene_api.MyGeneInfo()
    response = api.querymany(missing_list, scopes="refseq", species="human")
    gene_map = dict()
    [get_gene_symbol(gene=gene, gene_map=gene_map) for gene in response]
    return gene_map


def get_gene_symbol(gene, gene_map):
    if "notfound" not in gene:
        gen_symbol = gene["symbol"]
        refseq = gene["query"]
        gene_map[refseq] = gen_symbol
