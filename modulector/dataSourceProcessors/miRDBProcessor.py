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
import numpy as np
import pandas as pandas
from django.db import connection
from django.utils.timezone import make_aware

django.setup()  # TODO: explain why
from modulector.models import MirnaSource


# TODO: analyse/explain why not to use ThreadPool instead of Queue
# TODO: use logging package instead of print in production

lock = Lock()  # TODO: Explain why


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
    # file_path = os.path.join(parent_dir, "files/test2.txt")
    # file_path = os.path.join(parent_dir, "files/testFile.txt")
    manager = Manager()
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
    print("file loaded")
    split = np.array_split(filtered_data, 10000)
    pool = ThreadPoolExecutor(max_workers=10000)
    pool.map(partial(process_df, mirna_source=mirna_source, queue=queue), split)
    pool.shutdown(wait=True)
    end = time.time()
    print("termino carga de datos tardo seg " + str(end - start))
    start = time.time()
    print("arranca queries")
    runQueries(queue=queue)
    end = time.time()
    print("termino queries tardo seg " + str(end - start))
    mirna_source.synchronization_date = make_aware(mirna_source.synchronization_date.now())
    mirna_source.save()


def process_df(df, mirna_source, queue):
    array = df.to_numpy()
    if array.size != 0:
        [save_record(row, mirna_source, queue) for row in array]


def getOrCreateMirna(mirna_code):
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
    return result[0]


def save_record(row, mirna_source, queue):
    mirna = row[0]
    gen = row[1]
    score = round(Decimal.from_float(row[2]), 4)
    try:
        mirna_id = getOrCreateMirna(mirna)
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
        save_record(row, mirna_source, queue)


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
