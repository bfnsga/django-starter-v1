# Generated by Django 4.1.4 on 2023-01-29 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('organization_id', models.UUIDField()),
                ('filename_disk', models.CharField(max_length=128, unique=True)),
                ('filename_download', models.CharField(max_length=128, unique=True)),
                ('type', models.CharField(max_length=128)),
                ('uploaded_by', models.UUIDField()),
                ('uploaded_on', models.CharField(max_length=128)),
                ('modified_by', models.UUIDField()),
                ('modified_on', models.CharField(max_length=128)),
                ('filesize', models.IntegerField()),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
            ],
        ),
    ]
