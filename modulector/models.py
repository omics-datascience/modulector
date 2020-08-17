from django.db import models
from django.db.models import UniqueConstraint


class Mirna(models.Model):
    id = models.BigAutoField(primary_key=True)
    mirna_code = models.CharField(max_length=200, db_index=True)


class MirnaSource(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    site_url = models.CharField(max_length=200)
    min_score = models.DecimalField(max_digits=20, decimal_places=4)
    max_score = models.DecimalField(max_digits=20, decimal_places=4)
    score_interpretation = models.TextField(null=True)
    description = models.TextField(blank=True, null=True)
    synchronization_date = models.DateTimeField()
    file_type = models.CharField(max_length=50)
    file_separator = models.CharField(max_length=4)


class MirnaColumns(models.Model):
    id = models.BigAutoField(primary_key=True)
    mirna_source = models.ForeignKey(MirnaSource, related_name="mirnacolumns", on_delete=models.CASCADE)
    position = models.BigIntegerField(blank=True, null=True)
    column_name = models.CharField(max_length=100, blank=True, null=True)
    field_to_map = models.CharField(max_length=50, blank=True, null=True)


class MirnaXGen(models.Model):
    id = models.BigAutoField(primary_key=True)
    mirna = models.ForeignKey(Mirna, on_delete=models.CASCADE)
    gen = models.CharField(max_length=50, db_index=True)
    score = models.DecimalField(max_digits=20, decimal_places=4)
    pubmed_id = models.CharField(max_length=100, null=True)
    pubMedUrl = models.CharField(max_length=300, null=True)
    mirna_source = models.ForeignKey(MirnaSource, on_delete=models.CASCADE)
    UniqueConstraint(fields=["mirna", "gen", "source"], name='idx_unique_mirnaxgen')
