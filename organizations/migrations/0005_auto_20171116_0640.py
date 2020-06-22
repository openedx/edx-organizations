# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0004_auto_20170413_2315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='short_name',
            field=models.CharField(help_text="Please do not use any spaces or special characters in short name. This short name will be used in the course's course key.", max_length=255, verbose_name=u'Short Name', db_index=True),
        ),
    ]
