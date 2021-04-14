import logging
import os
import pathlib
import sys

from django.core import mail
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string

from ModulectorBackend.settings import UNSUBSCRIBE_URL, DEFAULT_FROM_EMAIL

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

parent_dir = pathlib.Path(__file__).parent.absolute().parent
html_template_path = os.path.join(parent_dir, "templates/email_template.html")
html_template_end = os.path.join(parent_dir, "templates/email_end.html")
html_rows_path = os.path.join(parent_dir, "templates/email_row.html")

html_template = render_to_string(html_template_path)
html_end = render_to_string(html_template_end)


def build_unsubscribe_url(unsubscribe_token):
    return UNSUBSCRIBE_URL + unsubscribe_token


def generate_link(link, text):
    return '<a href=\"{}\" target=\"_blank\">{}</a><br>'.format(link, text)


def build_url_to_send(pubmed_id):
    return 'https://pubmed.ncbi.nlm.nih.gov/' + str(pubmed_id)


def build_pubmeds(pubmeds):
    text = ''
    for pubmed_id in pubmeds:
        text = text + generate_link(build_url_to_send(pubmed_id), pubmed_id)
    return text


def email_users(content):
    subject = 'Update regarding your multiomix subscription'
    email_messages = []
    logger.info('Starting to build emails to send')
    for key in content:
        if len(content[key]) < 1:
            logger.info('empty info for {}, skipping'.format(key))
            continue
        rows = []
        for mail_row in content[key]:
            mirna = mail_row.mirna
            gene = mail_row.gene
            pubmeds = build_pubmeds(mail_row.pubmeds)
            token = mail_row.token
            url = build_unsubscribe_url(token)
            url = generate_link(url, 'unsubscribe')
            html_row = render_to_string(html_rows_path,
                                        {"mirna": mirna, "gene": gene, "unsubscribe": "{{ unsubscribe }}"
                                            , "pubmeds": "{{ pubmeds }}"})
            html_row = html_row.replace("{{ unsubscribe }}", url).replace("{{ pubmeds }}",
                                                                          pubmeds)
            rows.append(html_row)
        rows_data = ' '.join(rows)
        final_content = html_template + rows_data + html_end
        message = EmailMessage(subject=subject, to=[key], body=final_content, from_email=DEFAULT_FROM_EMAIL)
        message.content_subtype = "html"
        email_messages.append(message)
        logger.info('Appended email to {}'.format(message.to))
    for email in email_messages:
        logger.info(email)
    if len(email_messages) > 0:
        logger.info('Sending emails')
        with mail.get_connection(fail_silently=False) as connection:
            connection.send_messages(email_messages)
        logger.info('Emails sent')
    else:
        logger.info('skipping emails')
