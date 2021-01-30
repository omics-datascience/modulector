from collections import namedtuple

from modulector.utils import link_builder

function_dict = {
    'mirbase': link_builder.build_link_mirdb,
    'rnacentral': link_builder.build_link_rnacentral,
    'targetminer': link_builder.build_link_targetminer
}


def build_urls(mirna_id):
    UrlItem = namedtuple("UrlItem", "source, url")
    urls = []
    url_templates = link_builder.get_templates()
    if mirna_id:
        for index, name, url in url_templates:
            url_string = function_dict.get(name)(mirna_id, url)
            item = UrlItem(source=name, url=url_string)
            urls.append(item._asdict())
    return urls
