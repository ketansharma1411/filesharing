# Generated by Django 4.2 on 2025-01-11 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileupload',
            name='file_url',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='fileupload',
            name='file_id',
            field=models.CharField(default='<function uuid4 at 0x000001906DDB4040>', max_length=150),
        ),
    ]
