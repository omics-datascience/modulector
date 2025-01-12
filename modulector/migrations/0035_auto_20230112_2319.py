# Generated by Django 3.1.13 on 2023-01-04 18:55
import os
import pathlib
from django.db import migrations
import csv
import tqdm


def import_methylation_epic_v2(apps, _schema_editor):
    """
    Import the Illumina Infinium MethylationEPIC BeadChip (EPIC) V2 array database.
    The tables that are created are:
        modulector_methylation_epic_v2: basic info of the CpG methylation site
        modulector_methylation_ucsc_cpg_island: info relating the methylation site to the nearest CpG islands.
        modulector_methylation_ucsc_refgene: info relating the methylation site to other genetic information like genes and transcripts according to RefSeq
        modulector_methylation_gencode: info relating the methylation site to other genetic information such as genes and transcripts according to Gencode
    """
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    db_path = os.path.join(parent_dir, "files/EPIC.csv")  # Download DB from Infinium MethylationEPIC v2.0
    # Product Files in https://support.illumina.com/array/array_kits/infinium-methylationepic-beadchip-kit/downloads.html
    print("\nRemoving comments in file...")
    os.system('tail -n +8 ' + db_path + ' >modulector/files/tmp_db.csv')  # Removes first 7 rows

    print("\nGetting Django models...")
    MethylationEPIC = apps.get_model(app_label='modulector', model_name='MethylationEPIC')
    MethylationUCSC_CPGIsland = apps.get_model(app_label='modulector', model_name='MethylationUCSC_CPGIsland')
    MethylationUCSCRefGene = apps.get_model(app_label='modulector', model_name='MethylationUCSCRefGene')
    MethylationGencode = apps.get_model(app_label='modulector', model_name='MethylationGencode')

    print("Removing old data...")
    MethylationEPIC.objects.all().delete()
    MethylationUCSC_CPGIsland.objects.all().delete()
    MethylationUCSCRefGene.objects.all().delete()
    MethylationGencode.objects.all().delete()

    print("Processing DB and uploading data...")
    with open("modulector/files/tmp_db.csv", "r") as record:
        csvreader_object = csv.DictReader(record, dialect='excel', delimiter=",")
        for row in tqdm.tqdm(csvreader_object):
            if row["IlmnID"].startswith("cg"):
                methyl_site = MethylationEPIC.objects.create(
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
                len_islands_values = len(islands_values)
                len_relation_values = len(relation_values)
                if len_islands_values == len_relation_values and len_relation_values > 0:
                    islands = [
                        MethylationUCSC_CPGIsland(
                            ucsc_cpg_island_name=islands_values[i],
                            relation_to_ucsc_cpg_island=relation_values[i],
                            methylation_epic_v2_ilmnid=methyl_site
                        )
                        for i in range(0, len_relation_values)
                        if islands_values[i].startswith("chr")
                    ]
                    MethylationUCSC_CPGIsland.objects.bulk_create(islands)

                ucscrefseq_group_values = row["UCSC_RefGene_Group"].split(";")
                ucscrefseq_name_values = row["UCSC_RefGene_Name"].split(";")
                ucscrefseq_accession_values = row["UCSC_RefGene_Accession"].split(";")
                len_ucscrefseq_group_values = len(ucscrefseq_group_values)
                len_ucscrefseq_name_values = len(ucscrefseq_name_values)
                len_ucscrefseq_accession_values = len(ucscrefseq_accession_values)
                if len_ucscrefseq_group_values == len_ucscrefseq_name_values and len_ucscrefseq_name_values == len_ucscrefseq_accession_values:
                    ucscrefseq = [
                        MethylationUCSCRefGene(
                            ucsc_refgene_group=ucscrefseq_group_values[u],
                            ucsc_refgene_name=ucscrefseq_name_values[u],
                            ucsc_refgene_accession=ucscrefseq_accession_values[u],
                            methylation_epic_v2_ilmnid=methyl_site
                        )
                        for u in range(0, len_ucscrefseq_name_values)
                        if len(ucscrefseq_group_values[u]) > 0
                    ]
                    MethylationUCSCRefGene.objects.bulk_create(ucscrefseq)

                gencode_group_values = row["GencodeV41_Group"].split(";")
                gencode_name_values = row["GencodeV41_Name"].split(";")
                gencode_accession_values = row["GencodeV41_Accession"].split(";")
                len_gencode_group_values = len(gencode_group_values)
                len_gencode_name_values = len(gencode_name_values)
                len_gencode_accession_values = len(gencode_accession_values)
                if len_gencode_group_values == len_gencode_name_values and len_gencode_name_values == len_gencode_accession_values:
                    gencode = [
                        MethylationGencode(
                            gencode_group=gencode_group_values[i],
                            gencode_name=gencode_name_values[i],
                            gencode_accession=gencode_accession_values[i],
                            methylation_epic_v2_ilmnid=methyl_site
                        )
                        for i in range(0, len_gencode_name_values)
                        if len(gencode_group_values[i]) > 0
                    ]
                    MethylationGencode.objects.bulk_create(gencode)

    os.remove("modulector/files/tmp_db.csv")


class Migration(migrations.Migration):
    dependencies = [
        ('modulector', '0034_methylationepic_methylationgencode_methylationucsc_cpgisland_methylationucscrefgene'),
    ]

    operations = [
        migrations.RunPython(import_methylation_epic_v2)  # it takes about 2 hours
    ]
