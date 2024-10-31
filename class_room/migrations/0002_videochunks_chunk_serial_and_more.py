# Generated by Django 5.1.1 on 2024-10-29 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('class_room', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='videochunks',
            name='chunk_serial',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='videochunks',
            name='video_chunk',
            field=models.FileField(upload_to='video_chunks/'),
        ),
    ]