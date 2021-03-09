from collections import namedtuple
from typing import List, Dict
from modulector.utils import link_builder

function_dict = {
    'mirbase': link_builder.build_link_mirdb
}


def build_urls(mirna_id: str) -> List[Dict]:
    """
    Generates a list of sources links for a specific miRNA
    :param mirna_id: miRNA id
    :return: List of sources links
    """
    UrlItem = namedtuple("UrlItem", "source, url")
    urls = []
    url_templates = link_builder.get_templates()
    if mirna_id:
        for index, name, url in url_templates:
            url_string = function_dict.get(name)(mirna_id, url)
            item = UrlItem(source=name, url=url_string)
            urls.append(item._asdict())
    return urls
