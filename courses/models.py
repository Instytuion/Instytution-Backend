

from django.db import models
from cloudinary.models import CloudinaryField
from accounts.models import CustomUser
from accounts.constants import NOT_AVAILABLE


class ModelTrackeBaseClass(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        related_name='%(class)s_created',
        on_delete=models.SET_DEFAULT,
        default=NOT_AVAILABLE
    )
    updated_by = models.ForeignKey( 
        CustomUser,
        related_name='%(class)s_updated',
        on_delete=models.SET_DEFAULT,
        default=NOT_AVAILABLE
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

class LessonImage(ModelTrackeBaseClass):
    image = CloudinaryField('image', blank=True, null=True)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Lesson Image'
        verbose_name_plural = 'Lesson Images'

class LessonVideo(ModelTrackeBaseClass):
    name = models.CharField(max_length=50, unique=True)
    video = CloudinaryField('video', blank=True, null=True)

    class Meta:
        verbose_name = 'Lesson Video'
        verbose_name_plural = 'Lesson Videos'

class LessonPDF(ModelTrackeBaseClass):
    name = models.CharField(max_length=50, unique=True)
    pdf = CloudinaryField('pdf', blank=True, null=True)

    class Meta:
        verbose_name = 'Lesson PDF'
        verbose_name_plural = 'Lesson PDFs'

class Lesson(ModelTrackeBaseClass):
    name = models.CharField(max_length=50, unique=True)
    course = models.ForeignKey(
        'Course', 
        related_name='Lesson', 
        on_delete=models.SET_NULL,  
        null=True,  
        blank=True
    )
    week = models.IntegerField(null=True, blank=True)
    image = models.ManyToManyField(LessonImage, related_name='lessons')
    video = models.ManyToManyField(LessonVideo, related_name='lessons')
    chapter = models.ManyToManyField(LessonPDF, related_name='lessons')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'week'], name='unique_lesson_week')
        ]


    
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
        on_delete=models.SET_DEFAULT, 
        default=NOT_AVAILABLE
    )
    duration = models.IntegerField()
    image = CloudinaryField('image')
    description = models.TextField() 
    skill = models.CharField(max_length=250)
    prerequisite = models.CharField(max_length=250)
    lesson = models.ManyToManyField(
        Lesson, 
        related_name='course_lessons',
        blank=True
    )
    course_level = models.CharField(
        max_length=12, 
        choices=LEVEL_CHOICES, 
        default='beginner'
    )

    def __str__(self):
        return self.name

class Batch(ModelTrackeBaseClass):
    TIME_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
    ]
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
        on_delete=models.SET_DEFAULT, 
        default=NOT_AVAILABLE
    )
    start_date = models.DateField()
    end_date = models.DateField()
    time_slot = models.CharField(
        max_length=10,
        choices=TIME_CHOICES,
        default='morning'
    )

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