import os
import pathlib

import pandas as pandas

parent_dir = pathlib.Path(__file__).parent.absolute().parent

pub_med_file = os.path.join(parent_dir, "files/pubmed_file.xlsx")


def execute():
    pubmed_data = pandas.read_excel(io=pub_med_file, usecols=[1, 8], names=['MIRNA', 'PUBMED'])
    return pubmed_data.set_index('MIRNA').to_dict()['PUBMED']


def build_url(pubmed_id):
    return 'https://pubmed.ncbi.nlm.nih.gov/' + str(pubmed_id)
