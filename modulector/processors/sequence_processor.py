import logging
import os
import pathlib
import sys

import pandas as pd
from django.db import transaction, connection

from modulector.models import Mirna

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


def process():
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    file_path = os.path.join(parent_dir, "files/miraccs.csv")
    logger.info("loading sequence info")
    mirna_table = Mirna._meta.db_table
    update_template = "UPDATE {} set mirna_sequence= '{}' where mirna_code = '{}'"

    # loading files
    data = pd.read_csv(filepath_or_buffer=file_path, encoding="ISO-8859-1")

    with transaction.atomic():
        updates = []
        for index, row in data.iterrows():
            mirna, sequence = row
            updates.append(update_template.format(mirna_table, sequence, mirna))
        for update in updates:
            with connection.cursor() as cursor:
                cursor.execute(update)
        logger.info("mirna sequence updated")
