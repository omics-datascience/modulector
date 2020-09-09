import concurrent
import logging
import os
import pathlib
import queue
import time
from concurrent.futures._base import ALL_COMPLETED
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from decimal import Decimal
from functools import partial
from multiprocessing import Manager
from threading import Lock
from typing import List

import django
import mygene as gene_api
import numpy as np
import pandas as pandas
from django.db import connection, transaction
from django.utils.timezone import make_aware

django.setup()  # TODO: explain why
from modulector.models import MirnaSource, MirnaXGen, Mirna

# TODO: analyse/explain why not to use ThreadPool instead of Queue
# TODO: use logging package instead of print in production

lock = Lock()  # TODO: Explain why

parent_dir = pathlib.Path(__file__).parent.absolute().parent
file_map = dict()
file_map["small"] = os.path.join(parent_dir, "files/testFile.txt")
file_map["medium"] = os.path.join(parent_dir, "files/test2.txt")
file_map["large"] = os.path.join(parent_dir, "files/miRDB_v6.0_prediction_result.txt")

def getn(q, n):
    result = q.get() + ";"
    try:
        while len(result) < n:
            result = result + q.get(block=False) + ";"
    except queue.Empty:
        pass
    return result


def process(source_id):
    source_id = 1
    file_path = file_map["large"]
    # data init
    manager = Manager()
    gene_map = manager.dict()
    queue = manager.Queue()
    skipped_queue = manager.Queue()


    print("loading data")
    start = time.time()
    mirna_source = MirnaSource.objects.get(id=source_id)
    series_names = mirna_source.mirnacolumns.order_by('position').values_list('field_to_map', flat=True)
    series_names = list(series_names)
    data = pandas.read_csv(filepath_or_buffer=file_path,
                           delimiter=mirna_source.file_separator, header=None, names=series_names)
    filtered_data = data[data["MIRNA"].str.contains("hsa")]
    print("file loaded, it took: " + str(time.time() - start))

    print("translating gene map")
    start = time.time()
    translateRefSec(filtered_data, gene_map=gene_map, skipped_queue=skipped_queue)
    print("translated genes, it took: " + str(time.time() - start))

    print("query insertion started ")
    start = time.time()
    grouped: pandas.DataFrame = filtered_data.groupby('MIRNA').aggregate(lambda tdf: tdf.unique().tolist())
    with transaction.atomic():

        print("mirna_gene delete start ")
        start = time.time()
        MirnaXGen.objects.filter(mirna_source=source_id).delete()
        print("mirna_gene delete stop: " + str(time.time() - start))

        for mirna_code, genes_and_scores in grouped.iterrows():
            # Para DEBUG:
            #genes, scores = genes_and_scores
            #print('miRNA code:', mirna_code)
            #print('Genes list:', genes)
            #print('Scores list:', scores)

            mirna_obj = get_or_create_mirna(mirna_code)

            # Aca si usamos SQL plano para ganar performance en la insercion
            mirna_id = mirna_obj.pk
            table_name = MirnaXGen._meta.db_table  # Obtenemos de manera dinamica el nombre de la tabla
            insert_query_prefix = f'INSERT INTO {table_name} (gen, score, mirna_source_id, mirna_id) VALUES '
            insert_statements: List[str] = []

            # Generamos todas las tuplas de insercion. NOTA: no se ponen los espacios entre las comas para ahorrar megas
            # de ancho de banda ya que esta sentencia SQL podria quedar muy muy grande
            # TODO: aca si queres podes meterle un split y hacer las inserciones en paralelo
            for gene, score in zip(genes_and_scores['GEN'], genes_and_scores['SCORE']):
                if gene in gene_map:
                    insert_statements.append(f'(\'{gene_map[gene]}\',{score},{source_id},{mirna_id})')

            # Juntamos todas las sentencias e insertamos
            insert_query = insert_query_prefix + ','.join(insert_statements)
            try:
                with connection.cursor() as cursor:
                    cursor.execute(insert_query)
            except Exception as e:
                logging.exception(e)
    end = time.time()
    print("query insertion finished, it took " + str(end - start))
    mirna_source.synchronization_date = make_aware(mirna_source.synchronization_date.now())
    mirna_source.save()
    print("total skipped " + str(skipped_queue.qsize()))
    saveSkipped(skipped_queue)


def get_or_create_mirna(mirna_code):
    mirna_in_db = Mirna.objects.filter(mirna_code=mirna_code)
    if not mirna_in_db.exists():
        mirna_obj = Mirna(mirna_code=mirna_code)
        mirna_obj.save()
    else:
        mirna_obj = mirna_in_db.get()
    return mirna_obj


def saveChunk(data):
    try:
        with connection.cursor() as cursor:
            cursor.execute(data)
    except Exception as ex:
        print(ex)
        print('query to db failed')


def translateRefSec(df, gene_map, skipped_queue):
    api = gene_api.MyGeneInfo()
    unique_series = df["GEN"].drop_duplicates()
    start = time.time()
    data = unique_series.to_numpy()
    if len(data) == 0:
        return
    print("pegada a la api de genes")
    response = api.querymany(data, scopes="refseq", species="human")
    end = time.time()
    print("la pegada a la api tardo: " + str(end-start) + " segs")
    [getGeneSymbol(gen=gen, gene_map=gene_map, skipped_queue=skipped_queue) for gen in response]


def getGeneSymbol(gen, gene_map, skipped_queue):
    if "notfound" not in gen:
        gen_symbol = gen["symbol"]
        refseq = gen["query"]
        gene_map[refseq] = gen_symbol
    else:
        skipped_queue.put(gen["query"])



def saveSkipped(queue):
    pool = ThreadPoolExecutor(max_workers=1000)
    futures = []
    while not queue.empty():
        futures.append(pool.submit(save_file, getn(queue, 1000)))
    concurrent.futures.wait(futures, timeout=None, return_when=ALL_COMPLETED)
    pool.shutdown(wait=True)


def save_file(record):
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    file_path = os.path.join(parent_dir, "files/skipped.txt")
    with open(file_path, 'a') as f:
        f.write("%s" % record)
