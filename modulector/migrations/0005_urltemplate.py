# Generated by Django 3.0.8 on 2020-09-25 00:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('modulector', '0004_mirbaseidmirna'),
    ]

    operations = [
        migrations.CreateModel(
            name='UrlTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('url', models.CharField(max_length=100)),
            ],
        ),
        migrations.RunSQL("INSERT INTO MODULECTOR_URLTEMPLATE(NAME, URL) "
                          "VALUES ('mirdb','http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc=VALUE')"),
        migrations.RunSQL("INSERT INTO MODULECTOR_URLTEMPLATE(NAME, URL) "
                          "VALUES ('rnacentral','https://rnacentral.org/search?q=VALUE%20species:%22Homo%20sapiens%22')"),
        migrations.RunSQL("INSERT INTO MODULECTOR_URLTEMPLATE(NAME, URL) "
                          "VALUES ('microrna','http://www.microrna.org/linkFromMirbase.do?mirbase=VALUE')"),
        migrations.RunSQL("INSERT INTO MODULECTOR_URLTEMPLATE(NAME, URL) "
                          "VALUES ('targetscan','http://www.targetscan.org/cgi-bin/mirgene.cgi?mirg=VALUE')"),
        migrations.RunSQL("INSERT INTO MODULECTOR_URLTEMPLATE(NAME, URL) "
                          "VALUES ('targetminer','http://www.isical.ac.in/~bioinfo_miu/final_html_targetminer/VALUE.html')"),
        migrations.RunSQL("INSERT INTO MODULECTOR_URLTEMPLATE(NAME, URL) "
                          "VALUES ('quickgo','https://www.ebi.ac.uk/QuickGO/"
                          "services/annotation/search?geneProductId=VALUE')")

    ]