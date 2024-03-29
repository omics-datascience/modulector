import logging
import os
import pathlib
import sys
from typing import Final, List, Dict, Union
from django.core import mail
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from ModulectorBackend.settings import UNSUBSCRIBE_URL, DEFAULT_FROM_EMAIL, DEBUG

# Sets some logging configuration
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

parent_dir: Final[pathlib.Path] = pathlib.Path(__file__).parent.absolute().parent
html_template_path: Final[str] = os.path.join(parent_dir, "templates/email_template.html")
html_template_end: Final[str] = os.path.join(parent_dir, "templates/email_end.html")
html_rows_path: Final[str] = os.path.join(parent_dir, "templates/email_row.html")

html_template: Final[str] = render_to_string(html_template_path)
html_end: Final[str] = render_to_string(html_template_end)


def build_unsubscribe_url(unsubscribe_token: str) -> str:
    """Generates an unsubscribe url for a given token."""
    return UNSUBSCRIBE_URL + unsubscribe_token


def generate_link(link: str, text: Union[str, int]) -> str:
    """Generates an HTML link (as _blank)."""
    return f'<a href="{link}" target="_blank">{text}</a><br>'


def build_url_to_send(pubmed_id: int) -> str:
    """Generates a URL to send to the user."""
    return f'https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}'


def build_pubmeds(pubmeds: List[int]) -> str:
    """Builds the HTML for the pubmeds. Generates some links concatenated."""
    return ''.join([
        generate_link(build_url_to_send(pubmed_id), pubmed_id) for pubmed_id in pubmeds
    ])


def email_users(content: Dict):
    subject = 'Update regarding your multiomix subscription'
    email_messages = []

    logger.info('Starting to build emails to send')
    for key in content:
        if len(content[key]) < 1:
            logger.info('Empty info for {}, skipping'.format(key))
            continue
        rows = []
        for mail_row in content[key]:
            mirna = mail_row.mirna
            gene = mail_row.gene
            pubmeds = build_pubmeds(mail_row.pubmeds)
            token = mail_row.token
            url = build_unsubscribe_url(token)
            url = generate_link(url, 'unsubscribe')
            html_row = render_to_string(
                html_rows_path,
                {"mirna": mirna, "gene": gene, "unsubscribe": "{{ unsubscribe }}", "pubmeds": "{{ pubmeds }}"}
            )
            html_row = html_row.replace("{{ unsubscribe }}", url).replace("{{ pubmeds }}", pubmeds)
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
        logger.info('Sending emails...')
        with mail.get_connection(fail_silently=False) as connection:
            connection.send_messages(email_messages)
        logger.info('Emails sent')
    else:
        logger.info('Skipping emails...')
