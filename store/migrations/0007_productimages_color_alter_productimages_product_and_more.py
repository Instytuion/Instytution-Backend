# Generated by Django 5.1.1 on 2024-10-18 06:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_productsubcategories_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='productimages',
            name='color',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='productimages',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='store.products'),
        ),
        migrations.AlterUniqueTogether(
            name='productimages',
            unique_together={('product', 'color')},
        ),
    ]
