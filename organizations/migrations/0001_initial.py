from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.CharField(max_length=255, verbose_name='Long name', db_index=True)),
                ('short_name', models.CharField(max_length=255, db_index=True)),
                ('description', models.TextField()),
                ('logo', models.ImageField(help_text='Please add only .PNG files for logo images.', max_length=255, null=True, upload_to='organization_logos', blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationCourse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('course_id', models.CharField(max_length=255, db_index=True)),
                ('active', models.BooleanField(default=True)),
                ('organization', models.ForeignKey(to='organizations.Organization', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Link Course',
                'verbose_name_plural': 'Link Courses',
            },
        ),
        migrations.AlterUniqueTogether(
            name='organizationcourse',
            unique_together={('course_id', 'organization')},
        ),
    ]
