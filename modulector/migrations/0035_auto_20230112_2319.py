# Generated by Django 3.1.13 on 2023-01-04 18:55

import os
import pathlib
from django.db import migrations
import csv
import tqdm


def import_methylation_epic_v2(apps, schema_editor):
    """ Importa la base de datos del array de Illumina Infinium MethylationEPIC BeadChip (EPIC) V2
    Las tablas que se crea son:
        modulector_methylation_epic_v2: info basica del sitio de metilacion CpG
        modulector_methylation_ucsc_cpg_island: info que relaciona el sitio de metilacion con las islas CpG mas cercanas
        modulector_methylation_ucsc_refgene: info que relaciona el sitio de metilacion con otra informacion genetica como genes y transcriptos segun RefSeq
        modulector_methylation_gencode: info que relaciona el sitio de metilacion con otra informacion genetica como genes y transcriptos segun Gencode
    """
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    db_path = os.path.join(parent_dir, "files/EPIC-8v2-0_A1.csv")  # Download DB from Infinium MethylationEPIC v2.0
    # Product Files in https://support.illumina.com/array/array_kits/infinium-methylationepic-beadchip-kit/downloads
    # .html
    print("\nEliminando lineas de comentarios...")
    os.system('tail -n +8 ' + db_path + ' >modulector/files/tmp_db.csv')  # Elimino primeras 7 filas

    print("\nobteniendo modelo...")
    methylationepic = apps.get_model(app_label='modulector', model_name='MethylationEPIC')
    methylationisland = apps.get_model(app_label='modulector', model_name='MethylationUCSC_CPGIsland')
    methylationrefgene = apps.get_model(app_label='modulector', model_name='MethylationUCSCRefGene')
    methylationgencode = apps.get_model(app_label='modulector', model_name='MethylationGencode')

    print("proceso DB y cargo datos a tablas...")
    with open("modulector/files/tmp_db.csv", "r") as record:
        csvreader_object = csv.DictReader(record, dialect='excel', delimiter=",")
        for row in tqdm.tqdm(csvreader_object):
            if row["IlmnID"].startswith("cg"):
                methyl_site = methylationepic.objects.create(
                    ilmnid=row["IlmnID"],
                    name=row["Name"],
                    strand_fr=row["Strand_FR"],
                    chr=row["CHR"],
                    mapinfo=row["MAPINFO"],
                    methyl450_loci=row["Methyl450_Loci"],
                    methyl27_loci=row["Methyl27_Loci"],
                    epicv1_loci=row["EPICv1_Loci"]
                )

                islands_values = row["UCSC_CpG_Islands_Name"].split(";")
                relation_values = row["Relation_to_UCSC_CpG_Island"].split(";")
                leng_islands_values = len(islands_values)
                len_relation_values = len(relation_values)
                if leng_islands_values == len_relation_values and len_relation_values > 0:
                    for i in range(0, len_relation_values):
                        if islands_values[i].startswith("chr"):
                            methylationisland.objects.create(
                                ucsc_cpg_island_name=islands_values[i],
                                relation_to_ucsc_cpg_island=relation_values[i],
                                methylation_epic_v2_ilmnid=methyl_site
                            )

                ucscrefseq_group_values = row["UCSC_RefGene_Group"].split(";")
                ucscrefseq_name_values = row["UCSC_RefGene_Name"].split(";")
                ucscrefseq_accesion_values = row["UCSC_RefGene_Accession"].split(";")
                len_ucscrefseq_group_values = len(ucscrefseq_group_values)
                len_ucscrefseq_name_values = len(ucscrefseq_name_values)
                len_ucscrefseq_accesion_values = len(ucscrefseq_accesion_values)
                if len_ucscrefseq_group_values == len_ucscrefseq_name_values and len_ucscrefseq_name_values == len_ucscrefseq_accesion_values:
                    for i in range(0, len_ucscrefseq_name_values):
                        if len(ucscrefseq_group_values[i]) > 0:  # chequea que tenga algo, ya que puede ser un str vacio
                            methylationrefgene.objects.create(
                                ucsc_refgene_group=ucscrefseq_group_values[i],
                                ucsc_refgene_name=ucscrefseq_name_values[i],
                                ucsc_refgene_accession=ucscrefseq_accesion_values[i],
                                methylation_epic_v2_ilmnid=methyl_site
                            )

                        gencode_group_values = row["GencodeV41_Group"].split(";")
                        gencode_name_values = row["GencodeV41_Name"].split(";")
                        gencode_accesion_values = row["GencodeV41_Accession"].split(";")
                        len_gencode_group_values = len(gencode_group_values)
                        len_gencode_name_values = len(gencode_name_values)
                        len_gencode_accesion_values = len(gencode_accesion_values)
                        if len_gencode_group_values == len_gencode_name_values and len_gencode_name_values == len_gencode_accesion_values:
                            for i in range(0, len_gencode_name_values):
                                if len(gencode_group_values[
                                           i]) > 0:  # chequea que tenga algo, ya que puede ser un str vacio
                                    methylationgencode.objects.create(
                                        gencode_group=gencode_group_values[i],
                                        gencode_name=gencode_name_values[i],
                                        gencode_accession=gencode_accesion_values[i],
                                        methylation_epic_v2_ilmnid=methyl_site
                                    )

    os.remove("modulector/files/tmp_db.csv")


class Migration(migrations.Migration):
    dependencies = [
        ('modulector', '0034_methylationepic_methylationgencode_methylationucsc_cpgisland_methylationucscrefgene'),
    ]

    operations = [
        migrations.RunPython(import_methylation_epic_v2)  # TARDO 2hs!!!
    ]
