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
        item, created = SubscriptionItem.objects.get_or_create(mirna=mirna, gene=gene, subscription=subscription)
        if created:
            item.unsubscribe_token = unsubscribe_token
            item.save()
        else:
            unsubscribe_token = item.unsubscribe_token
    return unsubscribe_token


def unsubscribe_user(token):
    result = SubscriptionItem.objects.filter(unsubscribe_token=token).get()
    if result:
        with transaction.atomic():
            subscription = result.subscription
            result.delete()
            if SubscriptionItem.objects.filter(subscription=subscription).count() == 0:
                subscription.delete()
