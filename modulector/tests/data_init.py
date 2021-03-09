from datetime import datetime
from django.utils import timezone
from modulector.models import MirbaseIdMirna, UrlTemplate, Mirna, OldRefSeqMapping, GeneSymbolMapping, MirnaSource, \
    MirnaColumns, MirnaXGene, MirnaDisease, MirnaDrug


def load_test_data(cls):
    MirbaseIdMirna.objects.create(
        mirbase_accession_id='MIRBASETEST',
        mature_mirna='hsa-test-1'
    )
    UrlTemplate.objects.create(
        name='mirdb',
        url='test/url/com'
    )
    mirna = Mirna.objects.create(
        mirna_code='ASDAS_SDA@_SDASD'
    )
    OldRefSeqMapping.objects.create(
        old_value='NM_ASDAS',
        new_value='NMAS@!DS'
    )
    GeneSymbolMapping.objects.create(
        refseq='REFSEQEXAMPLE',
        symbol='SYMBOLTEST'
    )
    source = MirnaSource.objects.create(
        name='source',
        site_url='this_site_url',
        min_score=0,
        max_score=70,
        score_interpretation='this is a score interpretation',
        description='this is a description',
        synchronization_date=datetime.now(tz=timezone.utc),
        file_separator='t'
    )

    MirnaColumns.objects.create(
        mirna_source=source,
        position=1,
        column_name='column_name',
        field_to_map='field_to_map'

    )

    MirnaXGene.objects.create(
        mirna=mirna,
        gene='GEN_1',
        score=80,
        mirna_source=source
    )

    MirnaDisease.objects.create(
        category='CAT',
        mirna='MIRNA',
        disease='DIS',
        pubmed_id='12312312',
        description='this is a description'
    )

    MirnaDrug.objects.create(
        mature_mirna='ASSSDWA',
        mirbase_accession_id='NMAEASDE',
        small_molecule='SOME TEST',
        fda_approved=True,
        detection_method='detect method',
        condition='condition this',
        pubmed_id=2312,
        reference='reference ',
        support='suppport',
        expression_pattern='pattern'
    )
