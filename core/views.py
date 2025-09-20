# core/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
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

def login_view(request):
    """Handle student login"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        if not email or not password:
            return render(request, 'login.html', {
                'error': 'Please enter both email and password.'
            })
        
        try:
            # Find student by email
            student = Student.objects.get(email=email)
            
            # Check password
            if check_password(password, student.password):
                # Login successful - store in session
                request.session['student_id'] = str(student.student_id)
                request.session['student_name'] = student.name
                request.session['student_email'] = student.email
                messages.success(request, f'Welcome back, {student.name}!')
                return redirect('dashboard')  # Redirect to dashboard
            else:
                return render(request, 'login.html', {
                    'error': 'Invalid email or password.'
                })
                
        except Student.DoesNotExist:
            return render(request, 'login.html', {
                'error': 'Invalid email or password.'
            })
        
        except Exception as e:
            return render(request, 'login.html', {
                'error': 'Login failed. Please try again.'
            })
    
    return render(request, 'login.html')

def forgot_password(request):
    """Handle forgot password functionality"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validate input
        if not email or not new_password or not confirm_password:
            return render(request, 'forgot_password.html', {
                'error': 'Please fill all required fields.'
            })
        
        # Check if passwords match
        if new_password != confirm_password:
            return render(request, 'forgot_password.html', {
                'error': 'Passwords do not match.'
            })
        
        # Password strength validation
        if len(new_password) < 6:
            return render(request, 'forgot_password.html', {
                'error': 'Password must be at least 6 characters long.'
            })
        
        # Check if password has letters and numbers
        if not re.search(r'[A-Za-z]', new_password) or not re.search(r'\d', new_password):
            return render(request, 'forgot_password.html', {
                'error': 'Password must contain both letters and numbers.'
            })
        
        try:
            # Check if student exists
            student = Student.objects.get(email=email)
            
            # Update password (will be hashed automatically in save method)
            student.password = new_password
            student.save()
            
            messages.success(request, 'Password reset successfully! You can now login with your new password.')
            return redirect('login')
            
        except Student.DoesNotExist:
            return render(request, 'forgot_password.html', {
                'error': 'No account found with this email address.'
            })
        
        except Exception as e:
            return render(request, 'forgot_password.html', {
                'error': 'An error occurred. Please try again later.'
            })
    
    return render(request, 'forgot_password.html')

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
    
    # Strong password check
    if not re.search(r'[A-Za-z]', password1) or not re.search(r'\d', password1):
        return "Password must contain both letters and numbers."
    
    return None  # No errors

def dashboard(request):
    """Dashboard view with statistics and charts"""
    # Check if user is logged in
    if 'student_id' not in request.session:
        messages.error(request, 'Please login to access dashboard.')
        return redirect('login')
    
    from datetime import datetime
    from django.db.models import Count, Q
    from django.utils import timezone
    import json
    
    # Get selected year from request, default to current year
    selected_year = int(request.GET.get('year', datetime.now().year))
    
    # Get statistics
    total_students = Student.objects.filter(is_active=True).count()
    
    # Course-wise counts
    course_stats = Student.objects.filter(is_active=True).values('course').annotate(count=Count('id'))
    
    # Month-wise admissions for selected year - using a simpler approach
    monthly_admissions = []
    for month in range(1, 13):
        count = Student.objects.filter(
            admission_date__year=selected_year,
            admission_date__month=month,
            is_active=True
        ).count()
        monthly_admissions.append(count)
    
    # Prepare data for charts
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Prepare pie chart data
    pie_data = []
    for stat in course_stats:
        pie_data.append({
            'label': stat['course'],
            'value': stat['count']
        })
    
    # Get available years - using a safer approach
    try:
        all_students = Student.objects.filter(admission_date__isnull=False)
        years_set = set()
        for student in all_students:
            if student.admission_date:
                years_set.add(student.admission_date.year)
        available_years = sorted(years_set, reverse=True) if years_set else [datetime.now().year]
    except:
        available_years = [datetime.now().year]
    
    context = {
        'student_name': request.session.get('student_name', 'Student'),
        'total_students': total_students,
        'course_stats': course_stats,
        'monthly_data': json.dumps(monthly_admissions),
        'months': json.dumps(months),
        'pie_data': json.dumps(pie_data),
        'selected_year': selected_year,
        'available_years': available_years,
    }
    
    return render(request, 'dashboard.html', context)

def logout_view(request):
    """Handle logout"""
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def new_enquiry(request):
    """New Enquiry page with form"""
    if 'student_id' not in request.session:
        return redirect('login')
    
    from .models import Enquiry
    from datetime import datetime
    
    if request.method == 'POST':
        try:
            # Get form data
            student_name = request.POST.get('student_name', '').strip()
            mobile_no = request.POST.get('mobile_no', '').strip()
            course = request.POST.get('course', '')
            address = request.POST.get('address', '').strip()
            
            # Validation
            error = None
            if not student_name or len(student_name) < 2:
                error = "Student name must be at least 2 characters long."
            elif not mobile_no or len(mobile_no) != 10 or not mobile_no.isdigit():
                error = "Mobile number must be exactly 10 digits."
            elif not course:
                error = "Please select a course."
            elif not address or len(address) < 10:
                error = "Address must be at least 10 characters long."
            
            if error:
                return render(request, 'new_enquiry.html', {
                    'student_name': request.session.get('student_name'),
                    'error': error,
                    'form_data': {
                        'student_name': student_name,
                        'mobile_no': mobile_no,
                        'course': course,
                        'address': address
                    }
                })
            
            # Create enquiry
            enquiry = Enquiry.objects.create(
                student_name=student_name,
                mobile_no=mobile_no,
                course=course,
                address=address
            )
            
            messages.success(request, f'Enquiry created successfully! Enquiry No: {enquiry.enquiry_no}')
            return redirect('new_enquiry')
            
        except Exception as e:
            error = f"Failed to create enquiry: {str(e)}"
            return render(request, 'new_enquiry.html', {
                'student_name': request.session.get('student_name'),
                'error': error
            })
    
    # GET request - show form
    context = {
        'student_name': request.session.get('student_name'),
        'current_date': datetime.now().strftime('%Y-%m-%d')
    }
    return render(request, 'new_enquiry.html', context)

def enquiry_data(request):
    """View all enquiry data"""
    if 'student_id' not in request.session:
        return redirect('login')
    
    from .models import Enquiry
    
    enquiries = Enquiry.objects.all().order_by('-created_at')
    
    context = {
        'student_name': request.session.get('student_name'),
        'enquiries': enquiries,
        'total_enquiries': enquiries.count()
    }
    return render(request, 'enquiry_data.html', context)

def export_enquiries(request):
    """Export enquiries to Excel"""
    if 'student_id' not in request.session:
        return redirect('login')
    
    from .models import Enquiry
    import openpyxl
    from django.http import HttpResponse
    from datetime import datetime
    
    try:
        # Create workbook and worksheet
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Enquiries Data"
        
        # Headers
        headers = [
            'Enquiry No', 'Date', 'Student Name', 
            'Mobile No', 'Course', 'Address'
        ]
        
        # Write headers
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = openpyxl.styles.Font(bold=True)
            cell.fill = openpyxl.styles.PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        # Get all enquiries
        enquiries = Enquiry.objects.all().order_by('-created_at')
        
        # Write data
        for row, enquiry in enumerate(enquiries, 2):
            ws.cell(row=row, column=1, value=enquiry.enquiry_no)
            ws.cell(row=row, column=2, value=enquiry.enquiry_date.strftime('%d/%m/%Y'))
            ws.cell(row=row, column=3, value=enquiry.student_name)
            ws.cell(row=row, column=4, value=enquiry.mobile_no)
            ws.cell(row=row, column=5, value=enquiry.get_course_display())
            ws.cell(row=row, column=6, value=enquiry.address)
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        filename = f"enquiries_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Save workbook to response
        wb.save(response)
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting data: {str(e)}')
        return redirect('enquiry_data')

def new_admission(request):
    """New Admission page"""
    if 'student_id' not in request.session:
        return redirect('login')
    return render(request, 'new_admission.html', {
        'student_name': request.session.get('student_name')
    })

def fees_payment(request):
    """Fees Payment page"""
    if 'student_id' not in request.session:
        return redirect('login')
    return render(request, 'fees_payment.html', {
        'student_name': request.session.get('student_name')
    })

def students_details(request):
    """Students Details page"""
    if 'student_id' not in request.session:
        return redirect('login')
    
    students = Student.objects.filter(is_active=True).order_by('-admission_date')
    return render(request, 'students_details.html', {
        'student_name': request.session.get('student_name'),
        'students': students
    })