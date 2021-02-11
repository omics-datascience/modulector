import os
import pathlib

import pandas as pandas

parent_dir = pathlib.Path(__file__).parent.absolute().parent

pub_med_file = os.path.join(parent_dir, "files/pubmed_file.xlsx")


class PubmedDTO:
    def __init__(self, pubmed_id, pubmed_url, mirna, gene):
        self.pubmed_url = pubmed_url
        self.pubmed_id = pubmed_id
        self.mirna = mirna
        self.gene = gene


def execute():
    return pandas.read_excel(io=pub_med_file, engine='openpyxl',
                             usecols=[1, 3, 8], names=['MIRNA', 'GENE', 'PUBMED'])


def build_url(pubmed_id):
    return 'https://pubmed.ncbi.nlm.nih.gov/' + str(pubmed_id)


def build_pubmed_list(pubmed_data):
    pubmed_list = []
    for row in pubmed_data.iterrows():
        mirna, gene, pubmed_id = row[1]
        pubmed_list.append(PubmedDTO(pubmed_id, build_url(pubmed_id), mirna, gene))
    return pubmed_list
