from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0005_auto_20171116_0640'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='short_name',
            field=models.CharField(help_text='Please do not use spaces or special characters. Only allowed special characters are period (.), hyphen (-) and underscore (_).', max_length=255, verbose_name='Short Name', db_index=True),
        ),
    ]
