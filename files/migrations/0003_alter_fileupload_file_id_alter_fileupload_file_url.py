# Generated by Django 4.2 on 2025-01-11 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0002_fileupload_file_url_alter_fileupload_file_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='file_id',
            field=models.CharField(default='<function uuid4 at 0x0000010FDA784040>', max_length=150),
        ),
        migrations.AlterField(
            model_name='fileupload',
            name='file_url',
            field=models.CharField(blank=True, max_length=450, null=True),
        ),
    ]
