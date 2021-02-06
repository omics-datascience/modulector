from modulector.models import MirbaseIdMirna, UrlTemplate


def get_mature_mirna(mirna_id):
    mature_mirna = MirbaseIdMirna.objects.filter(mature_mirna=mirna_id).first()
    if not mature_mirna:
        splitted = mirna_id.split('-')
        mature = splitted[0] + splitted[1] + splitted[2]
        mature_mirna = MirbaseIdMirna.objects.filter(mature_mirna__contains=mature).first()
    return mature_mirna


def build_link_mirdb(mirna_id, template):
    return template.replace("VALUE", mirna_id)


def build_link_rnacentral(mirna_id, template):
    mature = get_mature_mirna(mirna_id)
    return template.replace("VALUE", mature.mature_mirna)


def build_link_targetminer(mirna_id, template):
    mature = get_mature_mirna(mirna_id)
    return template.replace("VALUE", mature.mature_mirna)


def get_templates():
    return UrlTemplate.objects.all().values_list()


def build_pubmed_url(pubmed_id):
    return "https://pubmed.ncbi.nlm.nih.gov/" + str(pubmed_id) + "/"
