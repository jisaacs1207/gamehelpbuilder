# Generated by Django 3.2 on 2021-05-27 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parseradmin', '0003_alter_entry_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
