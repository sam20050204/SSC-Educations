from django.contrib import admin
from .models import Student, Enquiry

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'mobile', 'course', 'admission_date', 'is_active']
    list_filter = ['is_active', 'course', 'admission_date']
    search_fields = ['name', 'email', 'mobile']
    readonly_fields = ['student_id', 'date_registered', 'password']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'mobile')
        }),
        ('Course Information', {
            'fields': ('course', 'admission_date')
        }),
        ('Account Information', {
            'fields': ('student_id', 'is_active', 'date_registered')
        }),
        ('Security', {
            'fields': ('password',),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['email', 'mobile']
        return self.readonly_fields

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ['enquiry_no', 'student_name', 'mobile_no', 'course', 'enquiry_date', 'created_at']
    list_filter = ['course', 'enquiry_date', 'created_at']
    search_fields = ['enquiry_no', 'student_name', 'mobile_no']
    readonly_fields = ['enquiry_no', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Enquiry Information', {
            'fields': ('enquiry_no', 'enquiry_date')
        }),
        ('Student Details', {
            'fields': ('student_name', 'mobile_no', 'course', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )