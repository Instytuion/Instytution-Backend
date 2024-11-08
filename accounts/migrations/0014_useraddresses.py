# Generated by Django 5.1.1 on 2024-11-07 09:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAddresses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('house_name', models.CharField(max_length=100)),
                ('street_name_1', models.CharField(max_length=100)),
                ('street_name_2', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('pincode', models.CharField(max_length=10)),
                ('phone_number', models.CharField(max_length=13)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'indexes': [models.Index(fields=['user', 'pincode', 'phone_number'], name='accounts_us_user_id_7be990_idx')],
                'unique_together': {('user', 'pincode', 'phone_number')},
            },
        ),
    ]
