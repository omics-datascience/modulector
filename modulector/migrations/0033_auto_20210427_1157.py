# Generated by Django 3.0.8 on 2021-04-27 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modulector', '0032_auto_20210331_0014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptionitem',
            name='record_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]