# Generated by Django 3.0.8 on 2020-09-16 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modulector', '0002_oldrefseqmapping'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneSymbolMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refseq', models.CharField(max_length=40, unique=True)),
                ('symbol', models.CharField(max_length=20)),
            ],
        ),
    ]
