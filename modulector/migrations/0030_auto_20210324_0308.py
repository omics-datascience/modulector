# Generated by Django 3.0.8 on 2021-03-24 03:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modulector', '0029_subscription_subscriptionitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='record_date',
        ),
        migrations.AddField(
            model_name='subscriptionitem',
            name='record_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 24, 3, 8, 7, 864647)),
        ),
    ]