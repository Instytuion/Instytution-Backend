# Generated by Django 5.1.1 on 2024-10-01 15:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0026_rename_image_lesson_images_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lessonimage',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='lessonimage',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='lessonpdf',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='lessonpdf',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='lessonvideo',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='lessonvideo',
            name='updated_by',
        ),
        migrations.DeleteModel(
            name='Lesson',
        ),
        migrations.DeleteModel(
            name='LessonImage',
        ),
        migrations.DeleteModel(
            name='LessonPDF',
        ),
        migrations.DeleteModel(
            name='LessonVideo',
        ),
    ]
