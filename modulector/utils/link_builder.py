from modulector.models import UrlTemplate


def build_link_mirdb(mirna_id, template):
    return template.replace("VALUE", mirna_id)


def get_templates():
    return UrlTemplate.objects.all().values_list()


def build_pubmed_url(pubmed_id) -> str:
    """
    Generates a Pubmed URL from a Pubmed ID
    :param pubmed_id: Pubmed ID to concatenate to Pubmed URL
    :return: Pubmed URL
    """
    return "https://pubmed.ncbi.nlm.nih.gov/" + str(pubmed_id) + "/"
