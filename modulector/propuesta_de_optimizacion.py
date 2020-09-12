import logging
from typing import List
import pandas as pd
from modulector.models import Mirna, MirnaXGene, MirnaSource
from django.db import transaction, connection


def get_or_create_mirna(mirna_code):
    mirna_in_db = Mirna.objects.filter(mirna_code=mirna_code)
    if not mirna_in_db.exists():
        mirna_obj = Mirna(mirna_code=mirna_code)
        mirna_obj.save()
    else:
        mirna_obj = mirna_in_db.get()
    return mirna_obj


mirna_source_id = 4

# Hacer simplpemente get, en vez de filter y get //DONE
mirna_source = MirnaSource.objects.get(id=mirna_source_id)

# Con values_list podes hacer lo que hacias con un for loop
series_names = mirna_source.mirnacolumns.order_by('position').values_list('field_to_map', flat=True)
series_names = list(series_names)

# Archivo de prueba limitado a 2000 rows para hacer pruebas rapidas
data = pd.read_csv('/home/genaro/Proyectos/modulector-backend/modulector/files/pruebas_borrar.csv',
                    delimiter="\t", header=None, names=series_names, nrows=2000)

# TODO: aca quizas podrian renombrarse las columnas para que siempre sean MIRNA, GENE y SCORE, de manera que queda
# TODO: generico a cualquier tipo de nombre

# El filtro queda igual, estaba joya
filtered_data = data[data["MIRNA"].str.contains("hsa")]

# Agrupa y devuelve [<mirna>, <lista de genes y list de scores>]
grouped: pd.DataFrame = filtered_data.groupby('MIRNA').aggregate(lambda tdf: tdf.unique().tolist())

# Recorre realizando las operaciones necesarias
with transaction.atomic():
    # Borramos todos los miRNAs x Genes que habia con respecto al mirna actual. Analizar, pero para mi es totalmente
    # logico. Ademas con la transaccion aseguramos la integracion
    MirnaXGene.objects.filter(mirna_source=mirna_source_id).delete()

    for mirna_code, genes_and_scores in grouped.iterrows():
        # Para DEBUG:
        # genes, scores = genes_and_scores
        # print('miRNA code:', mirna_code)
        # print('Genes list:', genes)
        # print('Scores list:', scores)

        # Si no existe en la DB, lo inserta, aca no es necesario usar SQL plano ya que la performance de esta unica
        # operacion es re contra despreciable
        mirna_obj = get_or_create_mirna(mirna_code)

        # Aca si usamos SQL plano para ganar performance en la insercion
        mirna_id = mirna_obj.pk
        table_name = MirnaXGene._meta.db_table  # Obtenemos de manera dinamica el nombre de la tabla
        insert_query_prefix = f'INSERT INTO {table_name} (gene, score, mirna_source_id, mirna_id) VALUES '
        insert_statements: List[str] = []

        # Generamos todas las tuplas de insercion. NOTA: no se ponen los espacios entre las comas para ahorrar megas
        # de ancho de banda ya que esta sentencia SQL podria quedar muy muy grande
        # TODO: aca si queres podes meterle un split y hacer las inserciones en paralelo
        for gene, score in zip(genes_and_scores['GEN'], genes_and_scores['SCORE']):
            insert_statements.append(f'({gene},{score},{mirna_source_id},{mirna_id})')

        # Juntamos todas las sentencias e insertamos
        insert_query = insert_query_prefix + ','.join(insert_statements)

        try:
            with connection.cursor() as cursor:
                cursor.execute(insert_query)
        except Exception as e:
            logging.exception(e)
