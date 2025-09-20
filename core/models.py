# core/models.py
from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
import uuid

class Student(models.Model):
    """Model to store student registration data"""
    
    # Unique identifier
    student_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Personal Information
    name = models.CharField(max_length=100, verbose_name="Full Name")
    mobile = models.CharField(
        max_length=10, 
        validators=[RegexValidator(regex=r'^\d{10}$', message='Mobile number must be 10 digits')],
        unique=True,
        verbose_name="Mobile Number"
    )
    email = models.EmailField(unique=True, verbose_name="Email Address")
    
    # Password (hashed)
    password = models.CharField(max_length=128, verbose_name="Password")
    
    # Metadata
    date_registered = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['-date_registered']
    
    def __str__(self):
        return f"{self.name} - {self.email}"
    
    def save(self, *args, **kwargs):
        # Hash password before saving if it's not already hashed
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


# core/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from .models import Student
import re

def home(request):
    return render(request, "home.html")

def register(request):
    if request.method == "POST":
        try:
            # Get form data
            name = request.POST.get("name", "").strip()
            mobile = request.POST.get("mobile", "").strip()
            email = request.POST.get("email", "").strip().lower()
            password1 = request.POST.get("password1", "")
            password2 = request.POST.get("password2", "")
            
            # Validation
            error = validate_registration_data(name, mobile, email, password1, password2)
            
            if error:
                return render(request, "register.html", {"error": error})
            
            # Check if email already exists
            if Student.objects.filter(email=email).exists():
                return render(request, "register.html", {
                    "error": "Email address already registered. Please use a different email."
                })
            
            # Check if mobile already exists
            if Student.objects.filter(mobile=mobile).exists():
                return render(request, "register.html", {
                    "error": "Mobile number already registered. Please use a different number."
                })
            
            # Create new student
            student = Student.objects.create(
                name=name,
                mobile=mobile,
                email=email,
                password=password1  # Will be hashed automatically in save() method
            )
            
            # Success message
            messages.success(request, f'Registration successful! Welcome {name}!')
            return redirect("home")
            
        except IntegrityError as e:
            return render(request, "register.html", {
                "error": "Registration failed. Email or mobile number may already exist."
            })
        
        except Exception as e:
            return render(request, "register.html", {
                "error": "Registration failed. Please try again."
            })
    
    # GET request - show registration form
    return render(request, "register.html")


def validate_registration_data(name, mobile, email, password1, password2):
    """Validate registration form data"""
    
    # Name validation
    if not name or len(name) < 2:
        return "Name must be at least 2 characters long."
    
    if len(name) > 100:
        return "Name cannot exceed 100 characters."
    
    # Mobile validation
    if not mobile:
        return "Mobile number is required."
    
    if not re.match(r'^\d{10}$', mobile):
        return "Mobile number must be exactly 10 digits."
    
    # Email validation
    if not email:
        return "Email address is required."
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return "Please enter a valid email address."
    
    # Password validation
    if not password1:
        return "Password is required."
    
    if len(password1) < 6:
        return "Password must be at least 6 characters long."
    
    if password1 != password2:
        return "Passwords do not match."
    
    # Strong password check (optional - you can adjust requirements)
    if not re.search(r'[A-Za-z]', password1) or not re.search(r'\d', password1):
        return "Password must contain both letters and numbers."
    
    return None  # No errors


# core/admin.py
from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'mobile', 'date_registered', 'is_active']
    list_filter = ['is_active', 'date_registered']
    search_fields = ['name', 'email', 'mobile']
    readonly_fields = ['student_id', 'date_registered', 'password']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'mobile')
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