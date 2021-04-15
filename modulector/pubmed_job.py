import json
import logging
import sys
from datetime import datetime

from django.db.models import Count

from modulector.models import SubscriptionItem, Subscription
from modulector.services import mailing_service
from modulector.services.pubmed_service import build_search_term, query_parse_and_build_pumbeds, get_pubmed_info

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


class MailDataItem:
    def __init__(self, mirna, gene, pubmeds, token):
        self.mirna = mirna
        self.gene = gene
        self.pubmeds = pubmeds
        self.token = token


def should_include_pubmed(data, subscription_item, id):
    json_object = json.loads(data)
    date_string = json_object["result"][str(id)]["sortpubdate"]
    parsed_date = datetime.strptime(date_string, '%Y/%m/%d %H:%M')
    record_date = subscription_item.record_date.replace(tzinfo=None)
    result = record_date < parsed_date
    return result


def execute():
    try:
        # grouping the subscriptions by mirna and gene, null gene first
        logger.info('Starting pubmed job')
        result_set = SubscriptionItem.objects.values('mirna', 'gene').annotate(total=Count('id'))
        # temporal maps
        publications_map = dict()
        data_for_mail = dict()
        pubmed_cache = dict()
        # iterate each row and query the api with the search term built
        for row in result_set:
            mirna = row['mirna']
            gene = row['gene']
            logger.info('building search term')
            term = build_search_term(mirna, gene)
            # create list of pubmed ids
            logger.info('creating pubmeds with term {}'.format(term))
            pubmeds = query_parse_and_build_pumbeds(term, mirna, gene, None)
            logger.info('created pubmeds')
            publications_map[term] = pubmeds
        # retrieve all main subcriptions and iterate the items
        for sub in Subscription.objects.all():
            subscription_items = SubscriptionItem.objects.filter(subscription=sub)
            logger.info('subscriptions {}'.format(subscription_items))
            mail_rows = []
            for subscription_item in subscription_items:
                term = build_search_term(subscription_item.mirna, subscription_item.gene)
                # rebuild the search term for the subcription and retrieve the pubmeds from the map
                pubmeds_ids = publications_map[term]
                # object that represents a row in the table sent to the user
                mail_data_item = MailDataItem(mirna=mirna, gene=gene, pubmeds=[],
                                              token=subscription_item.unsubscribe_token)
                logger.info('building each pubmed')
                for index, pubmed_id in enumerate(pubmeds_ids):
                    data = get_pubmed_info(pubmed_id, pubmed_cache)
                    if should_include_pubmed(data, subscription_item, pubmed_id):
                        mail_data_item.pubmeds.append(pubmed_id)
                if len(mail_data_item.pubmeds) > 0:
                    subscription_item.record_date = datetime.now()
                    subscription_item.save()
                    mail_rows.append(mail_data_item)
            data_for_mail[sub.email] = mail_rows

        mailing_service.email_users(content=data_for_mail)
        logger.info('Finished pubmed job')
    except Exception as ex:
        logger.error('Exception on job', exc_info=True)
        logging.error(ex, exc_info=True)
        raise ex