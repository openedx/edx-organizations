# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(help_text='Please add only .PNG files for logo images. This logo will be used on certificates.', max_length=255, null=True, upload_to=b'organization_logos', blank=True),
        ),
    ]
