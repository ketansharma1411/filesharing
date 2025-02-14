# Generated by Django 4.2 on 2025-01-06 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_id', models.CharField(default='<function uuid4 at 0x000001FCA4931300>', max_length=150)),
                ('file', models.FileField(upload_to='uploads/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('project_name', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
    ]
