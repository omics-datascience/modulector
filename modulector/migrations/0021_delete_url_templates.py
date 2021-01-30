
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modulector', '0020_auto_20210130_0317'),
    ]

    operations = [
        migrations.RunSQL("delete from MODULECTOR_URLTEMPLATE where name in ('quickgo', 'microrna', 'targetscan')"),
        migrations.RunSQL("update MODULECTOR_URLTEMPLATE set name = 'mirbase' where name ='mirdb'")

    ]
