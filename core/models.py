# core/models.py
from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
# Add the complete Admission class (see artifact: admission_model)
import uuid
from datetime import datetime

class Student(models.Model):
    """Model to store student registration data"""
    
    COURSE_CHOICES = [
        ('MSCIT', 'MSCIT'),
        ('KLIC', 'KLIC'),
        ('CCC', 'CCC'),
        ('TALLY', 'Tally'),
        ('MS_OFFICE', 'MS Office'),
        ('OTHER', 'Other'),
    ]
    
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
    
    # Course Information
    course = models.CharField(max_length=50, choices=COURSE_CHOICES, default='MSCIT', verbose_name="Course")
    admission_date = models.DateTimeField(auto_now_add=True, verbose_name="Admission Date", null=True, blank=True)
    
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


class Enquiry(models.Model):
    """Model to store enquiry data"""
    
    COURSE_CHOICES = [
        ('MS-CIT', 'MS-CIT'),
        ('TALLY', 'Tally'),
        ('ADVANCE_EXCEL', 'Advance Excel'),
        ('IOT', 'IOT'),
        ('MOM', 'MOM'),
        ('SCRATCH', 'Scratch'),
        ('SARTHI', 'Sarthi'),
    ]
    
    # Auto-generated enquiry number
    enquiry_no = models.CharField(max_length=20, unique=True, editable=False)
    
    # Personal Information
    student_name = models.CharField(max_length=100, verbose_name="Student Name")
    mobile_no = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message='Mobile number must be 10 digits')],
        verbose_name="Mobile Number"
    )
    
    # Course and Address
    course = models.CharField(max_length=50, choices=COURSE_CHOICES, verbose_name="Course")
    address = models.TextField(verbose_name="Address")
    
    # Date
    enquiry_date = models.DateField(auto_now_add=True, verbose_name="Enquiry Date")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enquiries'
        verbose_name = 'Enquiry'
        verbose_name_plural = 'Enquiries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.enquiry_no} - {self.student_name}"
    
    def save(self, *args, **kwargs):
        if not self.enquiry_no:
            # Generate enquiry number: ENQ + YYYYMMDD + sequential number
            from datetime import datetime
            today = datetime.now()
            date_str = today.strftime('%Y%m%d')
            
            # Get count of enquiries created today
            today_enquiries = Enquiry.objects.filter(
                created_at__date=today.date()
            ).count()
            
            # Generate enquiry number
            seq_num = str(today_enquiries + 1).zfill(3)
            self.enquiry_no = f"ENQ{date_str}{seq_num}"
        
        super().save(*args, **kwargs)

# Add this to your core/models.py file


class Admission(models.Model):
    """Model to store student admission data"""
    
    INSTALLMENT_CHOICES = [
        ('1', '1 Installment'),
        ('2', '2 Installments'),
    ]
    
    # Auto-generated form number
    form_no = models.CharField(max_length=20, unique=True, editable=False)
    
    # Admission date
    admission_date = models.DateField(verbose_name="Admission Date")
    
    # Course
    course_name = models.CharField(max_length=100, verbose_name="Course Name")
    
    # Student personal information
    first_name = models.CharField(max_length=50, verbose_name="First Name")
    middle_name = models.CharField(max_length=50, verbose_name="Middle Name")
    last_name = models.CharField(max_length=50, verbose_name="Last Name")
    
    # Birth date
    birth_date = models.DateField(verbose_name="Birth Date")
    
    # Contact information
    mobile_own = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message='Mobile number must be 10 digits')],
        verbose_name="Mobile Number (Own)"
    )
    mobile_parents = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message='Mobile number must be 10 digits')],
        blank=True,
        null=True,
        verbose_name="Mobile Number (Parents)"
    )
    
    # Address and qualification
    address = models.TextField(verbose_name="Address")
    qualification = models.CharField(max_length=100, verbose_name="Current Qualification")
    
    # Fee installments
    installments = models.CharField(
        max_length=1,
        choices=INSTALLMENT_CHOICES,
        verbose_name="Fee Installments"
    )
    
    # Photo (optional)
    photo = models.ImageField(
        upload_to='admission_photos/',
        blank=True,
        null=True,
        verbose_name="Student Photo"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'admissions'
        verbose_name = 'Admission'
        verbose_name_plural = 'Admissions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.form_no} - {self.get_full_name()}"
    
    def get_full_name(self):
        """Return full name of student"""
        return f"{self.first_name} {self.middle_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        if not self.form_no:
            # Generate form number: SSC + YYYY + 4-digit sequential number
            today = datetime.now()
            year = today.strftime('%Y')
            
            # Get count of admissions this year
            year_admissions = Admission.objects.filter(
                created_at__year=today.year
            ).count()
            
            # Generate form number
            seq_num = str(year_admissions + 1).zfill(4)
            self.form_no = f"SSC{year}{seq_num}"
        
        super().save(*args, **kwargs)

    batch = models.CharField(
        max_length=7,
        verbose_name="Batch (Month-Year)",
        help_text="Batch month and year (e.g., 2025-01 for January 2025)"
    )
    
    # Fee fields
    total_fees = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=5000.00,
        verbose_name="Total Fees"
    )
    paid_fees = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Paid Fees"
    )

    def get_remaining_fees(self):
        return self.total_fees - self.paid_fees
    