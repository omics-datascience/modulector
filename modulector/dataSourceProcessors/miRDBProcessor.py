import concurrent
import os
import pathlib
import queue
import time
from concurrent.futures._base import ALL_COMPLETED
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import Manager
from typing import List
import mygene as gene_api
import pandas as pandas
from django.db import connection, transaction
from django.utils.timezone import make_aware
from modulector.models import MirnaSource, MirnaXGene, Mirna

# TODO: add documentation to all the functions and remove fixed data.
# TODO: use logging package instead of print in production as it'll run in a Thead.
# TODO: check if it's needed to save skipped data.
# TODO: remove time dependency and all its usage from this file.

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


def process(source_id: int):
    file_path = file_map["large"]

    # data init
    manager = Manager()
    gene_map = manager.dict()
    skipped_queue = manager.Queue()

    print("loading data")
    start = time.time()
    mirna_source = MirnaSource.objects.get(id=source_id)
    series_names = mirna_source.mirnacolumns.order_by('position').values_list('field_to_map', flat=True)
    series_names = list(series_names)
    print(f'Tiempo de obtencion de datos de source -> {time.time() - start} segundos')

    start = time.time()
    data = pandas.read_csv(filepath_or_buffer=file_path,
                           delimiter=mirna_source.file_separator, header=None, names=series_names)
    print(f'Tiempo de lectura del CSV -> {time.time() - start} segundos')

    start = time.time()
    filtered_data = data[data["MIRNA"].str.contains("hsa")]
    print(f'Tiempo de filtrado por hsa -> {time.time() - start} segundos')

    print("translating gene map")
    start = time.time()
    translateRefSec(filtered_data, gene_map=gene_map, skipped_queue=skipped_queue)
    print(f"Translated genes -> {time.time() - start} segundos")

    print("query insertion started ")
    grouped: pandas.DataFrame = filtered_data.groupby('MIRNA').aggregate(lambda tdf: tdf.unique().tolist())

    # Some insertion stuff
    table_name = MirnaXGene._meta.db_table  # Obtenemos de manera dinamica el nombre de la tabla
    insert_query_prefix = f'INSERT INTO {table_name} (gene, score, mirna_source_id, mirna_id) VALUES '

    with transaction.atomic():
        print("mirna_gene delete start ")
        start = time.time()
        MirnaXGene.objects.filter(mirna_source=mirna_source).delete()
        print(f"mirna_gene delete -> {time.time() - start} segundos")

        start = time.time()
        for mirna_code, genes_and_scores in grouped.iterrows():
            # Para DEBUG:
            #genes, scores = genes_and_scores
            #print('miRNA code:', mirna_code)
            #print('Genes list:', genes)
            #print('Scores list:', scores)

            mirna_obj = get_or_create_mirna(mirna_code)

            # Aca si usamos SQL plano para ganar performance en la insercion
            mirna_id: int = mirna_obj.pk
            insert_statements: List[str] = []

            # Generamos todas las tuplas de insercion. NOTA: no se ponen los espacios entre las comas para ahorrar megas
            # de ancho de banda ya que esta sentencia SQL podria quedar muy muy grande
            insert_template = "('{}',{}," + str(source_id) + "," + str(mirna_id) + ")"
            for gene, score in zip(genes_and_scores['GEN'], genes_and_scores['SCORE']):
                if gene in gene_map:
                    insert_statements.append(insert_template.format(gene_map[gene], score))

            # Juntamos todas las sentencias e insertamos
            insert_query = insert_query_prefix + ','.join(insert_statements)

            with connection.cursor() as cursor:
                cursor.execute(insert_query)
        print(f'{grouped.shape[0]} mirnas insertados en {time.time() - start} segundos')

        mirna_source.synchronization_date = make_aware(mirna_source.synchronization_date.now())
        mirna_source.save()

    # TODO: is this needed?
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
    [getGeneSymbol(gene=gene, gene_map=gene_map, skipped_queue=skipped_queue) for gene in response]


def getGeneSymbol(gene, gene_map, skipped_queue):
    if "notfound" not in gene:
        gen_symbol = gene["symbol"]
        refseq = gene["query"]
        gene_map[refseq] = gen_symbol
    else:
        skipped_queue.put(gene["query"])


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
