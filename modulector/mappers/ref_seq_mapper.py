import os
import pathlib

from django.db import transaction, connection

sqL_input = "files/ref_seq_translation.sql"


def execute():
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    path = os.path.join(parent_dir, sqL_input)
    with open(path, "r") as file:
        sql = file.read()

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("truncate table modulector_oldrefseqmapping")
                cursor.execute(sql)
