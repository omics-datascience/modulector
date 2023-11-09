import logging
import sys
from typing import Optional
from xml.etree import ElementTree
import requests
from ModulectorBackend.settings import DEFAULT_FROM_EMAIL, NCBI_API_KEY
from modulector.models import Pubmed

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)
tool = 'multiomix'
email = DEFAULT_FROM_EMAIL
search_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/' \
             'esearch.fcgi?db=pmc&term={}&tool={}&email={}&api_key=' + NCBI_API_KEY

pubmed_api_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={}&retmode=json&tool={}'\
                 '&email={}&api_key=' + NCBI_API_KEY


# pubmed_api_url = 'http://localhost:3000/?db=pubmed&id={}&retmode=json&tool={}&email={}' \
#                '&api_key=' + NCBI_API_KEY


def build_search_term(mirna: str, gene: str) -> str:
    """Generates an NCBI search term for a given miRNA and gene."""
    return mirna + ' AND ' + gene if gene else mirna


def query_parse_and_build_pumbeds(term: str, mirna: str, gene: str, timeout: Optional[int]):
    try:
        response = requests.get(search_url.format(term, tool, email), timeout=timeout)

        if response.status_code == 200:
            pubmed_ids = set()
            xml = ElementTree.fromstring(response.text)
            for child in list(xml):
                if child.tag == 'IdList':
                    for id_tag in list(child):
                        pubmed_ids.add(int(id_tag.text))

            query = Pubmed.objects.filter(mirna_code=mirna)
            if gene:
                query = query.filter(gene=gene)

            result = query.values('pubmed_id')
            for value in result:
                pubmed_ids.add(int(value['pubmed_id']))
            return pubmed_ids
        else:
            raise Exception('Response code from pubmed query was not 200, it was {}'.format(response.status_code))
    except Exception as ex:
        logger.error('query and parse failed')
        raise ex


def get_pubmed_info(id, cache):
    if id in cache:
        return cache.get(id)
    else:
        response = requests.get(pubmed_api_url.format(id, tool, email))
        if response.status_code == 200:
            cache[id] = response.text
            return response.text
        else:
            raise Exception('pubmed info call failed for id {}'.format(id))
