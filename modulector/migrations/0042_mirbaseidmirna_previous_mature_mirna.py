import os
import pathlib
from django.db import migrations, models, connection


def load_mirna_mature(apps, _schema_editor):
    """Truncates modulector_mirbaseidmirna and reloads it from files/mirna_mature.txt.
    Only rows where mature_mirna starts with 'hsa' are imported (homo sapiens).
    File columns (whitespace-separated): id, mature_mirna, [previous_mature_mirna], mirbase_accession_id, ...
    In some rows the previous_mature_mirna column is absent.
    If previous_mature_mirna contains multiple values separated by ';', one row is
    inserted for each value.
    """
    parent_dir = pathlib.Path(__file__).parent.absolute().parent
    file_path = os.path.join(parent_dir, "files", "mirna_mature.txt")

    print("\nReading mirna_mature.txt...")
    MirbaseIdMirna = apps.get_model(app_label='modulector', model_name='MirbaseIdMirna')

    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE modulector_mirbaseidmirna")

    batch_size = 5000
    records = []
    with open(file_path, encoding='utf-8', errors='replace') as input_stream:
        for line in input_stream:
            parts = line.split()
            if len(parts) < 3:
                continue

            mature_mirna = parts[1]
            if not mature_mirna.startswith('hsa'):
                continue

            if parts[2].startswith('MIMAT'):
                previous_mature_mirna = ''
                mirbase_accession_id = parts[2]
            else:
                previous_mature_mirna = parts[2]
                mirbase_accession_id = parts[3]

            previous_values = [value.strip() for value in previous_mature_mirna.split(';') if value.strip()]
            if not previous_values:
                previous_values = ['']

            for previous_value in previous_values:
                records.append(MirbaseIdMirna(
                    mirbase_accession_id=mirbase_accession_id,
                    mature_mirna=mature_mirna,
                    previous_mature_mirna=previous_value,
                ))

    print(f"Truncating modulector_mirbaseidmirna and loading {len(records)} hsa records...")
    for i in range(0, len(records), batch_size):
        MirbaseIdMirna.objects.bulk_create(records[i:i + batch_size])

    print(f"Done. {len(records)} records loaded into modulector_mirbaseidmirna.")


class Migration(migrations.Migration):
    dependencies = [
        ('modulector', '0041_auto_20240410_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='mirbaseidmirna',
            name='previous_mature_mirna',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.RunPython(load_mirna_mature, migrations.RunPython.noop),
    ]
