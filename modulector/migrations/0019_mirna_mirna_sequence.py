# Generated by Django 3.0.8 on 2021-01-28 00:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modulector', '0018_auto_20210118_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='mirna',
            name='mirna_sequence',
            field=models.CharField(max_length=40, null=True),
        ),
    ]
