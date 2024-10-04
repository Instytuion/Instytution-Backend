

from django.db import models
from cloudinary.models import CloudinaryField
from accounts.models import CustomUser
from accounts.constants import NOT_AVAILABLE
from django.core.validators import MaxValueValidator
from datetime import time


class ModelTrackeBaseClass(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        related_name='%(class)s_created',
        on_delete=models.CASCADE
    )
    updated_by = models.ForeignKey( 
        CustomUser,
        related_name='%(class)s_updated',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class Program(ModelTrackeBaseClass):
    name = models.CharField(max_length=50, unique=True)
    image = CloudinaryField('image', blank=False, null=False)

    class Meta:
        verbose_name = 'Program'
        verbose_name_plural = 'Programs'
    def __str__(self):
        return self.name

class Lesson(ModelTrackeBaseClass):
    name = models.CharField(max_length=50)
    course = models.ForeignKey(
        'Course', 
        related_name='Lessons', 
        on_delete=models.SET_NULL,  
        null=True,  
        blank=True
    )
    week = models.IntegerField(null=True, blank=True)
    description = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'week'], name='unique_lesson_week')
        ]

class LessonImage(ModelTrackeBaseClass):
    lesson = models.ForeignKey(Lesson, related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField('image', blank=True, null=True)


    class Meta:
        verbose_name = 'Lesson Image'
        verbose_name_plural = 'Lesson Images'

class LessonVideo(ModelTrackeBaseClass):
    lesson = models.ForeignKey(Lesson, related_name='videos', on_delete=models.CASCADE)
    video = CloudinaryField('video', blank=True, null=True)

    class Meta:
        verbose_name = 'Lesson Video'
        verbose_name_plural = 'Lesson Videos'

class LessonPDF(ModelTrackeBaseClass):
    lesson = models.ForeignKey(Lesson, related_name='pdfs', on_delete=models.CASCADE)
    pdf = CloudinaryField('pdf', blank=True, null=True)

    class Meta:
        verbose_name = 'Lesson PDF'
        verbose_name_plural = 'Lesson PDFs'
  
class Course(ModelTrackeBaseClass):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    program = models.ForeignKey(
        Program, 
        related_name='course_programs', 
        on_delete=models.CASCADE
    )
    duration = models.IntegerField()
    image = CloudinaryField('image')
    description = models.TextField() 
    skill = models.CharField(max_length=250)
    prerequisite = models.CharField(max_length=250)
    course_level = models.CharField(
        max_length=12, 
        choices=LEVEL_CHOICES, 
        default='beginner'
    )

    def __str__(self):
        return self.name

class Batch(ModelTrackeBaseClass):

    name = models.CharField(max_length=100, unique=True)
    course = models.ForeignKey(
        'Course', 
        related_name='batches', 
        on_delete=models.SET_NULL,  
        null=True, 
        blank=True 
    )
    instructor = models.ForeignKey(
        CustomUser, 
        related_name='instructed_batches', 
        on_delete=models.Case
    )
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(default=time(8, 0))  
    end_time = models.TimeField(default=time(10, 0))   # 
    strength = models.IntegerField(validators=[MaxValueValidator(50)], default=9)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'name'], name='unique_batch_course')
        ]

    def __str__(self):
        return f"{self.name} ({self.course.name})"

class Session(ModelTrackeBaseClass):

    batch = models.ForeignKey(
        Batch, 
        related_name='sessions', 
        on_delete=models.SET_NULL,  
        null=True,  
        blank=True
    )
    date = models.DateTimeField(null=True, blank=True)
    offline_video = CloudinaryField(
        'video',
        resource_type='video',
        null=True,  
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['batch', 'date'], name='unique_batch_date')
        ]
    
class CourseWeekDescription(ModelTrackeBaseClass):
    course = models.ForeignKey(
        'Course', 
        related_name='week_description', 
        on_delete=models.CASCADE
    )
    week = models.IntegerField(blank=False, null=False)
    description = models.TextField() 
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'week'], name='unique_course_week')
        ]

class BatchStudents(models.Model):
    batch = models.ForeignKey(
        'Batch', 
        related_name='batch_students', 
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        CustomUser, 
        related_name='enrolled_batches', 
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    