import os
import pathlib
from typing import List

import pandas as pd
from django.db import connection

input_file = "files/aliases.txt"


def process():
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    path = os.path.join(parent_dir, input_file)
    df = pd.read_csv(filepath_or_buffer=path, delimiter='\t', names=['mirbase_accession_id', 'mirna'])
    df = df[df['mirna'].str.contains('hsa')]
    insert_query_prefix = 'INSERT INTO modulector_mirbaseidmirna (mirbase_accession_id, mature_mirna) VALUES '
    insert_statements: List[str] = []
    insert_template = "('{}','{}')"
    for index, row in df.iterrows():
        mirbase_accession_id = row['mirbase_accession_id']
        mirna_list = row['mirna']
        for mirna in mirna_list.split(';'):
            if mirna:
                insert_statements.append(insert_template.format(mirbase_accession_id, mirna))
    insert_query = insert_query_prefix + ','.join(insert_statements)
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE modulector_mirbaseidmirna")
        cursor.execute(insert_query)
