import logging
import sys
from typing import Optional, Dict, Final, Set
from xml.etree import ElementTree
import requests
from ModulectorBackend.settings import DEFAULT_FROM_EMAIL, NCBI_API_KEY, DEBUG
from modulector.models import Pubmed

# Sets some logging configuration
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

# Adds some constants
TOOL: Final[str] = 'multiomix'
SEARCH_URL: Final[str] = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/' \
                         'esearch.fcgi?db=pmc&term={}&tool={}&email={}&api_key=' + NCBI_API_KEY

PUBMED_API_URL: Final[str] = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={}&' \
                             'retmode=json&tool={}&email={}&api_key=' + NCBI_API_KEY


def build_search_term(mirna: str, gene: str) -> str:
    """Generates an NCBI search term for a given miRNA and gene."""
    return mirna + ' AND ' + gene if gene else mirna


def query_parse_and_build_pumbeds(term: str, mirna: str, gene: str, timeout: Optional[int]) -> Set[str]:
    """
    Queries pubmed for a given term, parses the response and builds a list of pubmed ids.
    :param term: Search term.
    :param mirna: miRNA code.
    :param gene: Gene name.
    :param timeout: Timeout for the request.
    :return: List of pubmed ids.
    """
    try:
        response = requests.get(SEARCH_URL.format(term, TOOL, DEFAULT_FROM_EMAIL), timeout=timeout)

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

            pubmed_ids.update(query.values_list('pubmed_id', flat=True))
            return pubmed_ids
        else:
            raise Exception('Response code from pubmed query was not 200, it was {}'.format(response.status_code))
    except Exception as ex:
        logger.error('query and parse failed')
        raise ex


def get_pubmed_info(pubmed_id: str, cache: Dict[str, str]) -> Optional[str]:
    """
    Gets the pubmed info for a given pubmed id.
    :param pubmed_id: Pubmed id.
    :param cache: Dicts used as cache to store the results.
    :return: Pubmed info.
    :raises: Exception if the call to the pubmed api fails.
    """
    if pubmed_id in cache:
        return cache.get(pubmed_id)
    else:
        response = requests.get(PUBMED_API_URL.format(pubmed_id, TOOL, DEFAULT_FROM_EMAIL))
        if response.status_code == 200:
            cache[pubmed_id] = response.text
            return cache[pubmed_id]
        else:
            raise Exception(f'Pubmed info call failed for id {pubmed_id}')
