# Generated by Django 5.1.1 on 2024-10-29 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_alter_productsubcategories_name_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productsubcategories',
            unique_together=set(),
        ),
    ]
