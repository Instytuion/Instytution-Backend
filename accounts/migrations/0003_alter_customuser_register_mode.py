# Generated by Django 5.1.1 on 2024-09-10 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customuser_register_mode_alter_customuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='register_mode',
            field=models.CharField(),
        ),
    ]