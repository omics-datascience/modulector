import hashlib
from datetime import datetime

from django.db import transaction

from modulector.models import Subscription, SubscriptionItem

token_generator = hashlib.md5()


def subscribe_user(email, mirna, gene):
    now = datetime.now().__str__()
    token_generator.update((email + now).encode('utf8'))
    unsubscribe_token = token_generator.hexdigest()
    with transaction.atomic():
        subscription, created = Subscription.objects.get_or_create(email=email)
        if created:
            subscription.unsubscribe_token = unsubscribe_token
            subscription.save()
        SubscriptionItem.objects.get_or_create(mirna=mirna, gene=gene, subscription=subscription)
    return unsubscribe_token


def unsubscribe_user(email, token):
    result = Subscription.objects.filter(email=email).get()
    if result:
        if result.unsubscribe_token != token:
            # TODO throw exception
            print("mr wrong")
        result.delete()
