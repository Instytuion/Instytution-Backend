from django.contrib import admin
from .models import CoursePayment

@admin.register(CoursePayment)
class CoursePaymentAdmin(admin.ModelAdmin):
    list_display = ('batch', 'user', 'created_at', 'amount')
    search_fields = ('batch',)
    list_filter = ('batch', 'user', 'created_at')
