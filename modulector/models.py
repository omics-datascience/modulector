from django.db import models
from django.db.models import UniqueConstraint
# TODO: remove 'id' fields in all Models, let Django manage that


class Mirna(models.Model):
    id = models.BigAutoField(primary_key=True)
    mirna_code = models.CharField(max_length=200, db_index=True, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['mirna_code'], name='idx_mirna_code')
        ]


class MirnaSource(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    site_url = models.CharField(max_length=200)
    min_score = models.DecimalField(max_digits=20, decimal_places=4)
    max_score = models.DecimalField(max_digits=20, decimal_places=4)
    score_interpretation = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    synchronization_date = models.DateTimeField()
    file_type = models.CharField(max_length=50)  # TODO: use Choices
    file_separator = models.CharField(max_length=4)  # TODO: use Choices


class MirnaColumns(models.Model):
    id = models.BigAutoField(primary_key=True)
    mirna_source = models.ForeignKey(MirnaSource, related_name="mirnacolumns", on_delete=models.CASCADE)
    position = models.BigIntegerField(blank=True, null=True)
    column_name = models.CharField(max_length=100, blank=True, null=True)
    field_to_map = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['position']


# TODO: english please: Gene
class MirnaXGen(models.Model):
    id = models.BigAutoField(primary_key=True)
    mirna = models.ForeignKey(Mirna, on_delete=models.CASCADE)
    gen = models.CharField(max_length=50, db_index=True) # TODO: english please: Gene
    score = models.DecimalField(max_digits=20, decimal_places=4)
    pubmed_id = models.CharField(max_length=100, null=True)
    pubMedUrl = models.CharField(max_length=300, null=True)
    mirna_source = models.ForeignKey(MirnaSource, on_delete=models.CASCADE)
    UniqueConstraint(fields=["mirna", "gen", "source"], name='idx_unique_mirnaxgen')

    class Meta:
        indexes = [
            models.Index(fields=['mirna'], name='idx_mirna'),
            models.Index(fields=['gen'], name='idx_gen'),
            models.Index(fields=['mirna_source'], name="idx_mirna_source")
        ]
        db_table = 'modulector_mirnaxgen'
