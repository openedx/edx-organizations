# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_auto_20170221_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='short_name',
            field=models.CharField(max_length=255, verbose_name=u'Short Name', db_index=True),
        ),
        migrations.AlterField(
            model_name='organizationcourse',
            name='course_id',
            field=models.CharField(max_length=255, verbose_name=u'Course ID', db_index=True),
        ),
    ]
