from typing import List

from django.db import models


class DatasetSeparator(models.TextChoices):
    """Possible separators for datasets"""
    COMMA = ',', 'Comma'
    SEMICOLON = ';', 'Semicolon'
    TAB = '\t', 'Tab'
    COLON = ':', 'Colon'
    WHITE_SPACE = ' ', 'White space'


class MirbaseIdMirna(models.Model):
    mirbase_id = models.CharField(max_length=20)
    mature_mirna = models.CharField(max_length=30)


class UrlTemplate(models.Model):
    name = models.CharField(max_length=40)
    url = models.CharField(max_length=100)


class Mirna(models.Model):
    mirna_code = models.CharField(max_length=40, unique=True)
    mirna_sequence = models.CharField(max_length=40, null=True)

    @property
    def mirbase_id(self) -> List:
        return MirbaseIdMirna.objects.filter(mature_mirna__contains=self.mirna_code)[0]


class OldRefSeqMapping(models.Model):
    old_value = models.CharField(max_length=40, unique=True)
    new_value = models.CharField(max_length=40)


class GeneSymbolMapping(models.Model):
    refseq = models.CharField(max_length=40, unique=True)
    symbol = models.CharField(max_length=20)


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
    mirna_source = models.ForeignKey(MirnaSource, on_delete=models.CASCADE)

    @property
    def pubmed(self) -> List:
        return Pubmed.objects.filter(mirna_code=self.mirna.mirna_code, gene=self.gene)

    class Meta:
        db_table = 'modulector_mirnaxgen'


class Pubmed(models.Model):
    pubmed_id = models.CharField(max_length=100, null=True)
    pubmed_url = models.CharField(max_length=300, null=True)
    gene = models.CharField(max_length=50, null=True)
    mirna_code = models.CharField(max_length=40, null=True)


class MirnaDisease(models.Model):
    category = models.CharField(max_length=200, blank=False)
    mirna = models.CharField(max_length=50, blank=False)
    disease = models.CharField(max_length=200, blank=False)
    pubmed_id = models.DecimalField(max_digits=10, decimal_places=0, null=False)
    description = models.TextField(blank=False)

    @property
    def mirna_object(self) -> List:
        return Mirna.objects.filter(mirna_code__contains=self.mirna)

    class Meta:
        db_table = 'modulector_mirnadisease'


class MirnaDrugs(models.Model):
    mature_mirna = models.CharField(max_length=50, blank=False)
    mirbase_id = models.CharField(max_length=20)
    small_molecule = models.TextField()
    fda_approved = models.BooleanField()
    detection_method = models.CharField(max_length=100)
    condition = models.TextField(blank=False)
    pubmed_id = models.DecimalField(max_digits=10, decimal_places=0, null=False)
    reference = models.TextField(blank=False)
    support = models.TextField(blank=False)
    expression_pattern = models.CharField(max_length=30)

    @property
    def mirna_object(self) -> List:
        return Mirna.objects.filter(mirna_code__contains=self.mature_mirna)

    class Meta:
        db_table = 'modulector_mirnadrugs'
