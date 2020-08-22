# Generated by Django 3.0.8 on 2020-08-22 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modulector', '0005_auto_20200822_1213'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='mirna',
            index=models.Index(fields=['mirna_code'], name='idx_mirna_code'),
        ),
        migrations.AddIndex(
            model_name='mirnaxgen',
            index=models.Index(fields=['gen'], name='idx_gen'),
        ),
    ]
