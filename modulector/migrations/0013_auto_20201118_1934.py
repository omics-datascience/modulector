# Generated by Django 3.0.8 on 2020-11-18 19:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modulector', '0012_auto_20201022_0449'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mirnaxgene',
            old_name='pubMedUrl',
            new_name='pubmed_url',
        ),
    ]