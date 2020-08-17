import os
import pathlib
from decimal import Decimal

import pandas as pandas
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import make_aware

from modulector.models import Mirna, MirnaSource, MirnaXGen

count = 0


def process(source_id):
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    file_path = os.path.join(parent_dir, "files/miRDB_v6.0_prediction_result.txt")
    # file_path = os.path.join(parent_dir, "files/testFile.txt")
    data = pandas.read_csv(filepath_or_buffer=file_path,
                           delimiter="\t", header=None, names=["MIRNA", "GEN", "SCORE"])
    filtered_data = data[data["MIRNA"].str.contains("hsa")]
    mirna_source = MirnaSource.objects.filter(id=source_id).get()
    ##filtered_data.apply(lambda x: save_record(x.MIRNA, x.GEN, x.SCORE))
    array = filtered_data.to_numpy()
    updates = []
    inserts = []
    [save_record(mirna_source, row, updates, inserts) for row in array]
    mirna_source.synchronization_date = make_aware(mirna_source.synchronization_date.now())
    mirna_source.save()
    print(updates)
    print(inserts)


# def saveData(data_frame, mirna_source):
# for row in data_frame.iterrows():
#     row = row[1]
#     mirna_x_gen = MirnaXGen(mirna=mirna_from_db[0], gen=row.GEN, score=score)
#     mirna_x_gen.mirna_source = mirna_source
#     try:
#         mirna_x_gen_db = MirnaXGen.objects.get(mirna_id=mirna_from_db[0].id, mirna_source_id=mirna_source.id,
#                                                gen=row.GEN)
#         with connection.cursor() as cursor:
#             cursor.execute('Update modulector.modulector_mirnaxgen set score = %s '
#                            'where modulector_mirnaxgen.id=%s', [score, mirna_x_gen_db.id])
#     except ObjectDoesNotExist:
#         with connection.cursor() as cursor:
#             cursor.execute('Insert into modulector.modulector_mirnaxgen'
#                            '(gen, score, pubmed_id, pubMedUrl, mirna_source_id, mirna_id) '
#                            'values(%s, %s, %s, %s, %s, %s)', [row.GEN, score, None,
#                            None, mirna_source.id, mirna_from_db[0].id])
# mirna_source.synchronization_date = make_aware(mirna_source.synchronization_date.now())
# mirna_source.save()


def save_record(mirna_source, row, updates, inserts):
    mirna = row[0]
    gen = row[1]
    data_set_score = row[2]
    score = round(Decimal.from_float(data_set_score), 4)
    mirna_from_db = Mirna.objects.get_or_create(mirna_code=mirna, defaults={'mirna_code': mirna})[0]
    mirna_x_gen = MirnaXGen(mirna=mirna_from_db, gen=gen, score=score)
    mirna_x_gen.mirna_source = mirna_source
    try:
        mirna_x_gen_db = MirnaXGen.objects.get(mirna_id=mirna_from_db.id, mirna_source_id=mirna_source.id,
                                               gen=gen)
        updates.append(
            "Update modulector.modulector_mirnaxgen set score = {0} where modulector_mirnaxgen.id={1}".format(score,
                                                                                                              mirna_x_gen_db.id))

    except ObjectDoesNotExist:
        inserts.append(
            "Insert into modulector.modulector_mirnaxgen (gen, score, mirna_source_id, mirna_id) values({0}, {1}, {2}, {3})"
                .format(gen, score, mirna_source.id, mirna_from_db.id))
