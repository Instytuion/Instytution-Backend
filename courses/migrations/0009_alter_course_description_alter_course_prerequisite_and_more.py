# Generated by Django 5.1.1 on 2024-09-14 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_course_course_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='course',
            name='prerequisite',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='course',
            name='skill',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='courseweekdescription',
            name='description',
            field=models.TextField(),
        ),
    ]
