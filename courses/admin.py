from django.contrib import admin
from .models import (
    Program, 
    LessonImage, 
    LessonVideo, 
    LessonPDF, 
    Lesson, 
    Course, 
    Batch, 
    Session,
    CourseWeekDescription,
    BatchStudents
    )

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'updated_by', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_by', 'updated_by', 'created_at', 'updated_at')

@admin.register(LessonImage)
class LessonImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'updated_by', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_by', 'updated_by', 'created_at', 'updated_at')

@admin.register(LessonVideo)
class LessonVideoAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'updated_by', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_by', 'updated_by', 'created_at', 'updated_at')

@admin.register(LessonPDF)
class LessonPDFAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'updated_by', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_by', 'updated_by', 'created_at', 'updated_at')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'updated_by', 'created_at', 'updated_at')
    search_fields = ('name', )
    list_filter = ('created_by', 'updated_by', 'created_at', 'updated_at')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'program', 'duration', 'course_level', 'created_by', 'updated_by', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'skill', 'prerequisite')
    list_filter = ('created_by', 'updated_by', 'created_at', 'updated_at', 'program')

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'instructor', 'time_slot', 'start_date', 'end_date', 'created_by', 'updated_by', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_by', 'updated_by', 'created_at', 'updated_at', 'course', 'instructor')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('batch', 'created_by', 'updated_by', 'created_at', 'updated_at')
    search_fields = ('batch__name', 'date')
    list_filter = ('created_by', 'updated_by', 'created_at', 'updated_at', 'batch',  )


@admin.register(CourseWeekDescription)
class CourseWeekDescriptionAdmin(admin.ModelAdmin):
    list_display = ('course', 'week', 'created_by', 'updated_by', 'created_at', 'updated_at')
    search_fields = ('course', 'week',)
    list_filter = ('created_by', 'updated_by', 'created_at', 'updated_at', 'course', 'week')

@admin.register(BatchStudents)
class BatchStudentsAdmin(admin.ModelAdmin):
    list_display = ('batch', 'student')
    search_fields = ('batch', 'student',)
    list_filter = ('batch', 'student')