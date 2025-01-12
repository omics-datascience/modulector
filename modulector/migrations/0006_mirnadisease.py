# Generated by Django 3.0.8 on 2020-10-04 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modulector', '0005_urltemplate'),
    ]

    operations = [
        migrations.CreateModel(
            name='MirnaDisease',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=200)),
                ('mirna', models.CharField(max_length=50)),
                ('disease', models.CharField(max_length=200)),
                ('pmid', models.DecimalField(decimal_places=0, max_digits=10)),
                ('description', models.TextField()),
            ],
            options={
                'db_table': 'modulector_mirnadisease',
            },
        ),
    ]
