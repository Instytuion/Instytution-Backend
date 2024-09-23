# Generated by Django 5.1.1 on 2024-09-23 05:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0013_batch_unique_batch_course'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchStudents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batch_students', to='courses.batch')),
                ('created_by', models.ForeignKey(default='Not Available', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(default='Not Available', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='enrolled_batches', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(default='Not Available', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
