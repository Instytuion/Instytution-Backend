# Generated by Django 5.1.1 on 2024-10-28 10:10

import cloudinary.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='RatingImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image')),
                ('rating', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='accounts.rating')),
            ],
        ),
    ]