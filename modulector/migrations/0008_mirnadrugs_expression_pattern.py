# Generated by Django 3.0.8 on 2020-10-22 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modulector', '0007_mirnadrugs'),
    ]

    operations = [
        migrations.AddField(
            model_name='mirnadrugs',
            name='expression_pattern',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
    ]
