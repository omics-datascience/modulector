from django.db import models
# from django.db.models import UniqueConstraint


class DatasetSeparator(models.TextChoices):
    """Possible separators for datasets"""
    COMMA = ',', 'Comma'
    SEMICOLON = ';', 'Semicolon'
    TAB = '\t', 'Tab'
    COLON = ':', 'Colon'
    WHITE_SPACE = ' ', 'White space'


class Mirna(models.Model):
    mirna_code = models.CharField(max_length=40, unique=True)


class MirnaSource(models.Model):
    name = models.CharField(max_length=200)
    site_url = models.CharField(max_length=200)
    min_score = models.DecimalField(max_digits=20, decimal_places=4)
    max_score = models.DecimalField(max_digits=20, decimal_places=4)
    score_interpretation = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    synchronization_date = models.DateTimeField()
    file_separator = models.CharField(max_length=1, choices=DatasetSeparator.choices, default=DatasetSeparator.TAB)


class MirnaColumns(models.Model):
    mirna_source = models.ForeignKey(MirnaSource, related_name="mirnacolumns", on_delete=models.CASCADE)
    position = models.BigIntegerField(blank=True, null=True)
    column_name = models.CharField(max_length=100, blank=True, null=True)
    field_to_map = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['position']


class MirnaXGene(models.Model):
    mirna = models.ForeignKey(Mirna, on_delete=models.CASCADE)
    gene = models.CharField(max_length=50)
    score = models.DecimalField(max_digits=20, decimal_places=4)
    pubmed_id = models.CharField(max_length=100, null=True)
    pubMedUrl = models.CharField(max_length=300, null=True)
    mirna_source = models.ForeignKey(MirnaSource, on_delete=models.CASCADE)
    # UniqueConstraint(fields=["mirna", "gene", "source"], name='idx_unique_mirnaxgen')  # FIXME: it's not applying

    class Meta:
        db_table = 'modulector_mirnaxgen'
