import csv
import logging
import os
import pathlib
import sys
from fasta_reader import read_fasta

import pandas as pd
from django.db import transaction, connection

from modulector.models import Mirna
from modulector.serializers import get_mirna_from_accession

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


def process():
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    db_path = os.path.join(parent_dir, "files/mature.fa") # Download DB from mirbase for mature mirnas https://www.mirbase.org/ftp.shtml
    file_path = os.path.join(parent_dir, "files/miraccs-adapted.xlsx")

    # creo archivo miraccs-adapted.xlsx
    csv_mature_file = open(file_path, 'w')
    #data_mature_out = csv.writer(csv_mature_file, dialect='excel', delimiter='\t')
    data_mature_out = csv.writer(csv_mature_file)
    data_mature_out.writerow(['mimat', 'mirna', 'sequence'])
    for item in read_fasta(db_path):
        defline = item.defline
        if "Homo sapiens" in defline:
            data = defline.split(" ")
            mirbase_id = data[0]
            mimat_id = data[1]
            sequence = item.sequence
            data_mature_out.writerow([mimat_id, mirbase_id, sequence])
    csv_mature_file.close()

    logger.info("loading sequence info")
    mirna_table = Mirna._meta.db_table
    update_template = "UPDATE {} set mirna_sequence= '{}' where mirna_code in {}"

    mimat_map = dict()
    # loading files
    #data = pd.read_excel(io=file_path, usecols=[0, 1, 2], names=['mimat', 'mirna', 'sequence'])
    data = pd.read_csv(file_path, usecols=[0, 1, 2], names=['mimat', 'mirna', 'sequence'])
    data = data[data["mimat"].notnull()]
    with transaction.atomic():
        updates = []
        for index, row in data.iterrows():
            mimat, mirna, sequence = row
            if mimat not in mimat_map:
                mirnas = get_mirna_from_accession(mimat)
                mimat_map[mimat] = mirnas
            else:
                mirnas = mimat_map[mimat]
            mirna_values = []
            mirna_values.extend("(")
            for i, mirna in enumerate(mirnas):
                value = "'" + mirna + "'"
                if i != 0:
                    value = ", " + value
                mirna_values.extend(value)
            mirna_values.extend(")")
            mirna_values = ''.join(mirna_values)

            if mirna_values != "()":
                updates.append(update_template.format(mirna_table, sequence, mirna_values))
        logger.info(len(updates))
        for update in updates:
            with connection.cursor() as cursor:
                cursor.execute(update)
        logger.info("mirna sequence updated")
