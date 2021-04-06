import json
from datetime import datetime
from xml.etree import ElementTree

import requests
from django.db.models.aggregates import Count

from ModulectorBackend.settings import DEFAULT_FROM_EMAIL, NCBI_API_KEY
from modulector.models import SubscriptionItem, Subscription, Pubmed
from modulector.services import mailing_service

tool = 'modulector'
email = DEFAULT_FROM_EMAIL
search_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/' \
             'esearch.fcgi?db=pmc&term={}&tool={}&email={}&api_key=' + NCBI_API_KEY

pubmed_api_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={}&retmode=json&tool={}&email={}' \
                 '&api_key=' + NCBI_API_KEY


class MailDataItem:
    def __init__(self, mirna, gene, pubmeds, token):
        self.mirna = mirna
        self.gene = gene
        self.pubmeds = pubmeds
        self.token = token


def build_search_term(mirna, gene):
    term = ''
    if gene:
        term = mirna + ' AND ' + gene
    else:
        term = mirna
    return term


def query_parse_and_build_pumbeds(term, mirna, gene):
    response = requests.get(search_url.format(term, tool, email))
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
        raise Exception('get failed bitch')


def get_pubmed_info(id, cache):
    if id in cache:
        return cache.get(id)
    else:
        response = requests.get(pubmed_api_url.format(id, tool, email))
        if response.status_code == 200:
            cache[id] = response.text
            return response.text
        else:
            raise Exception('get failed bitch')


def should_include_pubmed(data, subscription_item, id):
    json_object = json.loads(data)
    date_string = json_object["result"][str(id)]["sortpubdate"]
    parsed_date = datetime.strptime(date_string, '%Y/%m/%d %H:%M')
    record_date = subscription_item.record_date.replace(tzinfo=None)
    return record_date < parsed_date


def execute():
    # grouping the subscriptions by mirna and gene, null gene first
    result_set = SubscriptionItem.objects.values('mirna', 'gene').annotate(total=Count('id'))
    # temporal maps
    publications_map = dict()
    data_for_mail = dict()
    pubmed_cache = dict()
    # iterate each row and query the api with the search term built
    for row in result_set:
        mirna = row['mirna']
        gene = row['gene']
        term = build_search_term(mirna, gene)
        # create list of pubmed ids
        pubmeds = query_parse_and_build_pumbeds(term, mirna, gene)
        publications_map[term] = pubmeds
    # retrieve all main subcriptions and iterate the items
    for sub in Subscription.objects.all():
        subscription_items = SubscriptionItem.objects.filter(subscription=sub)
        mail_rows = []
        for subscription_item in subscription_items:
            term = build_search_term(subscription_item.mirna, subscription_item.gene)
            # rebuild the search term for the subcription and retrieve the pubmeds from the map
            pubmeds_ids = publications_map[term]
            # object that represents a row in the table sent to the user
            mail_data_item = MailDataItem(mirna=mirna, gene=gene, pubmeds=[], token=subscription_item.unsubscribe_token)
            for index, pubmed_id in enumerate(pubmeds_ids):
                # if index < 2:
                # get the pubmed data and check if the
                data = get_pubmed_info(pubmed_id, pubmed_cache)
                if should_include_pubmed(data, subscription_item, pubmed_id):
                    mail_data_item.pubmeds.append(pubmed_id)
            if len(mail_data_item.pubmeds) > 0:
                ##subscription_item.record_date = datetime.now()
                ##subscription_item.save()
                mail_rows.append(mail_data_item)
        data_for_mail[sub.email] = mail_rows
    mailing_service.email_users(content=data_for_mail)
