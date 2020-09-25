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


def build_link_microrna(mirna_id, template):
    mature = get_mature_mirna(mirna_id)
    return template.replace("VALUE", mature.mirbase_id)


def build_link_targetscan(mirna_id, template):
    mature = get_mature_mirna(mirna_id)
    return template.replace("VALUE", mature.mature_mirna)


def build_link_targetminer(mirna_id, template):
    mature = get_mature_mirna(mirna_id)
    return template.replace("VALUE", mature.mature_mirna)


def build_link_quickgo(mirna_id, template):
    return ''


function_dict = {
    'mirdb': build_link_mirdb,
    'rnacentral': build_link_rnacentral,
    'microrna': build_link_microrna,
    'targetscan': build_link_targetscan,
    'targetminer': build_link_targetminer,
    'quickgo': build_link_quickgo
}


def build_urls(mirna_id):
    urls = dict()
    url_templates = UrlTemplate.objects.all().values_list()
    if mirna_id:
        for index, name, url in url_templates:
            result = function_dict.get(name)(mirna_id, url)
            urls[name] = result
    return urls
