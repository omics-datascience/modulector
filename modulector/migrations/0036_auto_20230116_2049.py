# Generated by Django 3.1.13 on 2023-01-04 18:55

import os
import pandas as pd
import pathlib
from django.db import migrations, connection
from fasta_reader import read_fasta


def import_mirbase(apps, schema_editor):
    """ Importa la base de datos mirBase a las tablas: modulector_mirna y modulector_mirbaseidmirna"""
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    db_mature_path = os.path.join(parent_dir, "files/mature.fa")  # Download DB from mirbase for mature mirnas
    db_hairpin_path = os.path.join(parent_dir, "files/hairpin.fa")  # Download DB from mirbase for hairpin mirnas
    # https://www.mirbase.org/ftp.shtml para descargar las dos DBs anteriores
    print("\nobteniendo modelos...")
    mirna = apps.get_model(app_label='modulector', model_name='Mirna')
    mirbaseidmirna = apps.get_model(app_label='modulector', model_name='MirbaseIdMirna')
    mirnaxgen = apps.get_model(app_label='modulector', model_name='MirnaXGene')
    num_registros_mirna = mirna.objects.all().count()
    num_registros_mirnaxgen = mirnaxgen.objects.all().count()
    print("borrando datos de mirbase (~" + str(num_registros_mirna*num_registros_mirnaxgen) + " registros)...")
    # mirna.objects.all().delete()  # Borro datos actuales en la tabla
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE modulector_mirna CASCADE")
    num_registros_mirbaseidmirna = mirna.objects.all().count()
    print("borrando datos de mirbase (" + str(num_registros_mirbaseidmirna) + " registros)...")
    mirbaseidmirna.objects.all().delete()  # Borro datos actuales en la tabla

    print("proceso archivo fasta de los mirnas matures y cargo datos de la ultima version...")
    for item in read_fasta(db_mature_path):
        defline = item.defline
        if "Homo sapiens" in defline:
            data = defline.split(" ")
            mirbase_id = data[0]
            mimat_id = data[1]
            sequence = item.sequence
            mirna.objects.create(mirna_code=mirbase_id, mirna_sequence=sequence)
            mirbaseidmirna.objects.create(mirbase_accession_id=mimat_id, mature_mirna=mirbase_id)

    print("proceso archivo fasta de los mirnas hairpin y cargo datos de la ultima version...")
    for item in read_fasta(db_hairpin_path):
        defline = item.defline
        if "Homo sapiens" in defline:
            data = defline.split(" ")
            mirbase_id = data[0]
            mimat_id = data[1]
            sequence = item.sequence
            mirna.objects.create(mirna_code=mirbase_id, mirna_sequence=sequence)
            mirbaseidmirna.objects.create(mirbase_accession_id=mimat_id, mature_mirna=mirbase_id)

    raise Exception('Prueba mirBase')


def import_mirdip(apps, schema_editor):
    """ Actualiza la base de datos mirdip en la tabla modulector_mirnaxgene
    Columns for file : files/mirDIP_Unidirectional_search_v.5.txt
        GENE_SYMBOL
        MICRORNA
        SOURCE_NUMBER
        INTEGRATED_RANK
        SOURCES
        SCORE_CLASS
    Ejemplo:
        "SPRYD3","hsa-miR-15a-5p",15,+9.11060805626107E-001,"Cupid|MBStar|MirTar2|MultiMiTar|PACCMIT|bitargeting_May_2021|miRTar2GO|MirAncesTar|miranda_May_2021|mirbase|miRDB_v6|mirmap_May_2021|MiRNATIP|mirzag|TargetScan_v7_2","V"
    """
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    mirdip_file_path = os.path.join(parent_dir, "files/mirDIP_Unidirectional_search_v.5.txt")

    print("\nobteniendo modelos...")
    mirnaxgene = apps.get_model(app_label='modulector', model_name='MirnaXGene')
    mirna = apps.get_model(app_label='modulector', model_name='Mirna')
    mirnasource = apps.get_model(app_label='modulector', model_name='MirnaSource')
    print("borrando datos de mirdip 4.1...")
    # mirnaxgene.objects.all().delete() #Borro datos actuales en la tabla
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE modulector_mirnaxgen")
    print("leyendo datos de mirdip 5.1...")
    mirdip_data = pd.read_csv(mirdip_file_path,
                              header=None,
                              names=['GENE_SYMBOL', 'MICRORNA', 'SOURCE_NUMBER', 'INTEGRATED_RANK', 'SOURCES',
                                     'SCORE_CLASS']
                              )  # esto tarda y ocupa mucha memoria porque le archivo es gigante

    print("cargando mirdip a la db...")
    source = mirnasource.objects.filter(name='mirdip')
    if not source:
        raise Exception('No se encuentra el source de name=mirdip en la tabla modulector_mirnasource')
    else:
        for _idx, row in mirdip_data.iterrows():
            # microrna = row['MICRORNA'].lower().replace("_","-")
            mirna_objects = mirna.objects.filter(mirna_code=row['MICRORNA'])
            if not mirna_objects:
                print('WARNING\t' + row['MICRORNA'] + ' NO SE ENCUENTRA EN MIRBASE. REGISTRO OMITIDO EN LA CARGA.')
                # raise Exception('El registro en la DB MirDIP tiene un valor de miRNA que no existe en la tabla '
                #                 'modulector_mirna. Valor: ' + row['MICRORNA'])
            else:
                mirnaxgene.objects.create(gene=row['GENE_SYMBOL'],
                                          score=row['INTEGRATED_RANK'],
                                          sources=row['SOURCES'],
                                          score_class=row['SCORE_CLASS'],
                                          mirna_source=source[0],  # si habria mas de uno, se podria asignar
                                          # cualquiera de los dos
                                          mirna=mirna_objects[0]  # siempre va  a ser el valor cero porque mirna_code
                                          # es unique en el modelo de datos Mirna
                                          )

    raise Exception('Prueba Mirdip')


class Migration(migrations.Migration):
    dependencies = [
        ('modulector', '0035_auto_20230112_2319'),
    ]

    operations = [
        migrations.RunPython(import_mirbase),
        # migrations.RunPython(import_mirdip)
    ]
