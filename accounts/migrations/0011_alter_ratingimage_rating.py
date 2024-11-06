# Generated by Django 5.1.1 on 2024-10-28 13:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_ratingimage_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratingimage',
            name='rating',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='accounts.rating'),
        ),
    ]
