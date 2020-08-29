import concurrent
import os
import pathlib
import queue
import time
from concurrent.futures._base import ALL_COMPLETED
from concurrent.futures.thread import ThreadPoolExecutor
from decimal import Decimal
from functools import partial
from multiprocessing import Manager
from threading import Lock

import django
import mygene as gene_api
import numpy as np
import pandas as pandas
from django.db import connection
from django.utils.timezone import make_aware

django.setup()
from modulector.models import MirnaSource

lock = Lock()


def getn(q, n):
    result = q.get() + ";"
    try:
        while len(result) < n:
            result = result + q.get(block=False) + ";"
    except queue.Empty:
        pass
    return result


def process(source_id):
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    file_path = os.path.join(parent_dir, "files/miRDB_v6.0_prediction_result.txt")
    #file_path = os.path.join(parent_dir, "files/test2.txt")
    #file_path = os.path.join(parent_dir, "files/testFile.txt")
    manager = Manager()
    mirna_map = dict()
    gene_map = dict()
    queue = manager.Queue()
    start = time.time()
    print("arranca carga de datos ")
    mirna_source = MirnaSource.objects.filter(id=source_id).get()
    series_names = []
    for item in mirna_source.mirnacolumns.all().order_by():
        series_names.append(item.field_to_map)

    data = pandas.read_csv(filepath_or_buffer=file_path,
                           delimiter="\t", header=None, names=series_names)
    filtered_data = data[data["MIRNA"].str.contains("hsa")]
    print("file loaded, it took: " + str(time.time() - start))
    print("analyzing mirnas")
    start = time.time()

    analyze_mirnas(filtered_data, mirna_map)
    print("analyzed mirnasit took: " + str(time.time() - start))

    print("translating gene map")
    start = time.time()
    pool = ThreadPoolExecutor(max_workers=1000)
    pool.map(partial(translateRefSec, gene_map=gene_map), np.array_split(filtered_data, 1000))
    pool.shutdown(wait=True)
    print("translated genes, it took: " + str(time.time() - start))

    print("generating queries")
    start = time.time()
    split = np.array_split(filtered_data, 10000)
    pool = ThreadPoolExecutor(max_workers=10000)
    pool.map(partial(process_df, mirna_source=mirna_source, queue=queue,
                     mirna_map=mirna_map, gene_map=gene_map), split)
    pool.shutdown(wait=True)
    end = time.time()
    print("queries generation  " + str(end - start))

    print("query insertion started ")
    start = time.time()
    runQueries(queue=queue)
    end = time.time()
    print("query insertion finished, it took " + str(end - start))
    mirna_source.synchronization_date = make_aware(mirna_source.synchronization_date.now())
    mirna_source.save()


def process_df(df, mirna_source, queue, mirna_map, gene_map):
    array = df.to_numpy()
    if array.size != 0:
        [generate_record(row, mirna_source, queue, mirna_map, gene_map) for row in array]


def getOrCreateMirna(mirna_code, mirna_map):
    with connection.cursor() as cursor:
        cursor.execute(
            "select id from modulector.modulector_mirna where mirna_code=%s ",
            [mirna_code])
        result = cursor.fetchone()
        if result is None:
            cursor.execute("Insert into modulector.modulector_mirna (mirna_code) values(%s)", [mirna_code])
            cursor.execute(
                "select id from modulector.modulector_mirna where mirna_code=%s ", [mirna_code])
            result = cursor.fetchone()
    mirna_map[mirna_code] = result[0]


def generate_record(row, mirna_source, queue, mirna_map, gen_map):
    mirna = row[0]
    gen = row[1]
    score = round(Decimal.from_float(row[2]), 4)
    try:
        mirna_id = mirna_map[mirna]
        gen = gen_map[gen]
        with connection.cursor() as cursor:
            cursor.execute(
                "select id from modulector.modulector_mirnaxgen where mirna_id = %s and mirna_source_id= %s and gen=%s",
                [mirna_id, mirna_source.id, gen])
            result = cursor.fetchone()
            if result is None:
                data = "Insert into modulector.modulector_mirnaxgen (gen, score, mirna_source_id, mirna_id) values('{0}', {1}, {2}, {3})".format(
                    gen, score, mirna_source.id, mirna_id)
            else:
                data = "Update modulector.modulector_mirnaxgen set score = {0} where modulector_mirnaxgen.id= {1}".format(
                    score, result[0])
            queue.put(data, block=False)
    except Exception as ex:
        print(ex)
        print("retry")
        time.sleep(1)
        generate_record(row, mirna_source, queue, mirna_map, gen_map)


def runQueries(queue):
    print("queue size:" + str(queue.qsize()))
    pool = ThreadPoolExecutor(max_workers=100)
    futures = []
    while not queue.empty():
        futures.append(pool.submit(saveChunk, getn(queue, 100)))
    concurrent.futures.wait(futures, timeout=None, return_when=ALL_COMPLETED)
    pool.shutdown(wait=True)


def saveChunk(data):
    try:
        with connection.cursor() as cursor:
            cursor.execute(data)
    except Exception as ex:
        print(ex)
        print('query to db failed')


def translateRefSec(df, gene_map):
    df["GEN"].drop_duplicates().apply(partial(getGeneSymbol, gene_map=gene_map))


def getGeneSymbol(gen, gene_map):
    try:
        response = gene_api.MyGeneInfo().query(gen)['hits']
        if len(response) == 0:
            gen_symbol = None
        else:
            gen_symbol = response[0]['symbol']
        gene_map[gen] = gen_symbol
    except Exception as ex:
        print("error during api call for id" + str(gen))
        print(ex)
        print(response)
        time.sleep(5)
        getGeneSymbol(gen, gene_map)


def analyze_mirnas(df, mirna_map):
    mirna_series = df["MIRNA"]
    mirna_series = mirna_series.drop_duplicates()
    mirna_series.apply(partial(getOrCreateMirna, mirna_map=mirna_map))
