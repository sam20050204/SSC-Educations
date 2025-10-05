# core/views.py - COMPLETE UPDATED VERSION

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from .models import Student, Enquiry, Admission, Payment
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
import json
from datetime import datetime
import re
from decimal import Decimal

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
                return redirect('dashboard')
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
    """Dashboard view with statistics and charts - UPDATED"""
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
    
    # Get statistics from Admission table (not Student table)
    total_students = Admission.objects.filter(is_active=True).count()
    
    # MSCIT students count
    mscit_count = Admission.objects.filter(
        is_active=True, 
        course_name='MS-CIT'
    ).count()
    
    # KLIC students count (all except MSCIT)
    klic_count = Admission.objects.filter(
        is_active=True
    ).exclude(course_name='MS-CIT').count()
    
    # Course-wise counts for all courses
    course_stats = Admission.objects.filter(is_active=True).values('course_name').annotate(count=Count('id'))
    
    # Month-wise admissions for selected year
    monthly_admissions = []
    for month in range(1, 13):
        count = Admission.objects.filter(
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
            'label': stat['course_name'],
            'value': stat['count']
        })
    
    # Get available years from admission records
    try:
        all_admissions = Admission.objects.filter(admission_date__isnull=False)
        years_set = set()
        for admission in all_admissions:
            if admission.admission_date:
                years_set.add(admission.admission_date.year)
        available_years = sorted(years_set, reverse=True) if years_set else [datetime.now().year]
    except:
        available_years = [datetime.now().year]
    
    context = {
        'student_name': request.session.get('student_name', 'Student'),
        'total_students': total_students,
        'mscit_count': mscit_count,
        'klic_count': klic_count,
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
    """Handle new student admission with complete form processing"""
    if 'student_id' not in request.session:
        messages.error(request, 'Please login to access this page.')
        return redirect('login')
    
    from datetime import datetime
    
    if request.method == 'POST':
        try:
            # Get form data
            admission_date = request.POST.get('admission_date', '').strip()
            batch = request.POST.get('batch', '').strip()
            course_name = request.POST.get('course_name', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            middle_name = request.POST.get('middle_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            birth_date = request.POST.get('birth_date', '').strip()
            mobile_own = request.POST.get('mobile_own', '').strip()
            mobile_parents = request.POST.get('mobile_parents', '').strip()
            address = request.POST.get('address', '').strip()
            qualification = request.POST.get('qualification', '').strip()
            installment = request.POST.get('installment', '')
            photo = request.FILES.get('photo')
            
            # Validation
            errors = []
            
            if not admission_date:
                errors.append("Admission date is required.")
            
            if not batch:
                errors.append("Please select a batch (month-year).")
            
            if not course_name:
                errors.append("Please select a course.")
            
            if not first_name or len(first_name) < 2:
                errors.append("First name must be at least 2 characters long.")
            
            if not middle_name or len(middle_name) < 2:
                errors.append("Middle name must be at least 2 characters long.")
            
            if not last_name or len(last_name) < 2:
                errors.append("Last name must be at least 2 characters long.")
            
            if not birth_date:
                errors.append("Birth date is required.")
            
            if not mobile_own or len(mobile_own) != 10 or not mobile_own.isdigit():
                errors.append("Own mobile number must be exactly 10 digits.")
            
            if mobile_parents and (len(mobile_parents) != 10 or not mobile_parents.isdigit()):
                errors.append("Parent mobile number must be exactly 10 digits.")
            
            if not address or len(address) < 10:
                errors.append("Address must be at least 10 characters long.")
            
            if not qualification:
                errors.append("Current qualification is required.")
            
            if not installment:
                errors.append("Please select a fee installment option.")
            
            if errors:
                error_message = " ".join(errors)
                messages.error(request, error_message)
                return render(request, 'new_admission.html', {
                    'student_name': request.session.get('student_name'),
                    'form_data': request.POST
                })
            
            # Create admission
            admission = Admission(
                admission_date=admission_date,
                batch=batch,
                course_name=course_name,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                birth_date=birth_date,
                mobile_own=mobile_own,
                mobile_parents=mobile_parents if mobile_parents else None,
                address=address,
                qualification=qualification,
                installments=installment,
                photo=photo,
                created_by=request.session.get('student_name', 'Admin')
            )
            
            admission.save()
            
            # Get full name for success message
            full_name = f"{first_name} {middle_name} {last_name}"
            
            # SUCCESS MESSAGE
            messages.success(
                request, 
                f'✅ Admission successful! Form No: {admission.form_no} | '
                f'Student: {full_name} | Course: {course_name} | Batch: {batch}'
            )
            
            return redirect('new_admission')
            
        except Exception as e:
            messages.error(request, f"Failed to process admission: {str(e)}")
            return render(request, 'new_admission.html', {
                'student_name': request.session.get('student_name'),
                'form_data': request.POST
            })
    
    # GET request
    return render(request, 'new_admission.html', {
        'student_name': request.session.get('student_name'),
        'today': datetime.now().strftime('%Y-%m-%d')
    })

def fees_payment(request):
    """Fees Payment page"""
    if 'student_id' not in request.session:
        messages.error(request, 'Please login to access this page.')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Get form data
            admission_id = request.POST.get('admission_id')
            amount_paid = request.POST.get('amount_paid')
            payment_mode = request.POST.get('payment_mode')
            transaction_ref = request.POST.get('transaction_ref', '')
            remarks = request.POST.get('remarks', '')
            
            # Validation
            if not admission_id or not amount_paid or not payment_mode:
                messages.error(request, 'Please fill all required fields.')
                return redirect('fees_payment')
            
            # Convert to Decimal
            amount_paid = Decimal(str(amount_paid))
            if amount_paid <= 0:
                messages.error(request, 'Amount must be greater than zero.')
                return redirect('fees_payment')
            
            # Get admission
            admission = Admission.objects.get(id=admission_id, is_active=True)
            
            # Check if amount exceeds remaining fees
            remaining = admission.total_fees - admission.paid_fees
            if amount_paid > remaining:
                messages.error(request, f'Amount exceeds remaining fees (₹{remaining}).')
                return redirect('fees_payment')
            
            # Create payment
            payment = Payment.objects.create(
                admission=admission,
                payment_date=datetime.now().date(),
                amount_paid=amount_paid,
                payment_mode=payment_mode,
                transaction_ref=transaction_ref if transaction_ref else None,
                remarks=remarks if remarks else None,
                created_by=request.session.get('student_name', 'Admin')
            )
            
            messages.success(
                request,
                f'✅ Payment successful! Receipt No: {payment.receipt_no} | '
                f'Amount: ₹{amount_paid} | Student: {admission.get_full_name()}'
            )
            
            # Return with receipt number for printing
            return redirect(f'/fees-payment/?receipt={payment.receipt_no}')
            
        except Admission.DoesNotExist:
            messages.error(request, 'Student not found.')
            return redirect('fees_payment')
        except Exception as e:
            messages.error(request, f'Payment failed: {str(e)}')
            return redirect('fees_payment')
    
    # GET request
    receipt_no = request.GET.get('receipt', None)
    context = {
        'student_name': request.session.get('student_name'),
        'today': datetime.now().strftime('%Y-%m-%d'),
        'receipt_no': receipt_no
    }
    return render(request, 'fees_payment.html', context)

def students_details(request):
    """Students Details page"""
    if 'student_id' not in request.session:
        return redirect('login')
    
    students = Student.objects.filter(is_active=True).order_by('-admission_date')
    return render(request, 'students_details.html', {
        'student_name': request.session.get('student_name'),
        'students': students
    })

def admitted_students(request):
    """View for admitted students page"""
    if 'student_id' not in request.session:
        messages.error(request, 'Please login to access this page.')
        return redirect('login')
    
    context = {
        'student_name': request.session.get('student_name', 'Teacher'),
    }
    return render(request, 'admitted_students.html', context)

def get_admitted_students(request):
    """API endpoint to get filtered students"""
    if 'student_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    course = request.GET.get('course', '')
    batch = request.GET.get('batch', '')
    
    if not course or not batch:
        return JsonResponse({'error': 'Course and batch are required'}, status=400)
    
    try:
        # Filter admissions by course and batch
        admissions = Admission.objects.filter(
            course_name=course,
            batch=batch,
            is_active=True
        ).order_by('first_name')
        
        # Prepare student data
        students_data = []
        for admission in admissions:
            students_data.append({
                'id': admission.id,
                'formNo': admission.form_no,
                'admissionDate': admission.admission_date.strftime('%Y-%m-%d'),
                'course': admission.course_name,
                'batch': admission.batch,
                'firstName': admission.first_name,
                'middleName': admission.middle_name,
                'lastName': admission.last_name,
                'birthDate': admission.birth_date.strftime('%Y-%m-%d'),
                'mobileOwn': admission.mobile_own,
                'mobileParents': admission.mobile_parents or '',
                'address': admission.address,
                'qualification': admission.qualification,
                'installments': admission.installments,
                'photo': admission.photo.url if admission.photo else None,
                'totalFees': float(admission.total_fees),
                'paidFees': float(admission.paid_fees),
                'remainingFees': float(admission.total_fees - admission.paid_fees)
            })
        
        return JsonResponse({
            'success': True,
            'students': students_data,
            'count': len(students_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def update_student(request):
    """API endpoint to update student data"""
    if 'student_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        student_id = data.get('id')
        
        if not student_id:
            return JsonResponse({'error': 'Student ID is required'}, status=400)
        
        # Get admission record
        admission = Admission.objects.get(id=student_id, is_active=True)
        
        # Update fields
        admission.first_name = data.get('firstName', admission.first_name)
        admission.middle_name = data.get('middleName', admission.middle_name)
        admission.last_name = data.get('lastName', admission.last_name)
        admission.birth_date = data.get('birthDate', admission.birth_date)
        admission.mobile_own = data.get('mobileOwn', admission.mobile_own)
        admission.mobile_parents = data.get('mobileParents', admission.mobile_parents)
        admission.address = data.get('address', admission.address)
        admission.qualification = data.get('qualification', admission.qualification)
        admission.total_fees = data.get('totalFees', admission.total_fees)
        admission.paid_fees = data.get('paidFees', admission.paid_fees)
        
        admission.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Student data updated successfully'
        })
        
    except Admission.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def delete_student_admission(request):
    """API endpoint to delete student admission and all related data"""
    if 'student_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        admission_id = data.get('admission_id')
        
        if not admission_id:
            return JsonResponse({'error': 'Admission ID is required'}, status=400)
        
        admission = Admission.objects.get(id=admission_id)
        student_name = admission.get_full_name()
        form_no = admission.form_no
        
        # Delete admission (related payments will be deleted automatically due to CASCADE)
        admission.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Student {student_name} (Form No: {form_no}) and all related data deleted successfully'
        })
        
    except Admission.DoesNotExist:
        return JsonResponse({'error': 'Student admission not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def search_student_for_payment(request):
    """API endpoint to search student by name"""
    if 'student_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        search_term = data.get('search_term', '').strip().lower()
        
        if not search_term or len(search_term) < 2:
            return JsonResponse({
                'success': True,
                'students': []
            })
        
        # Search in admissions
        admissions = Admission.objects.filter(
            is_active=True
        ).filter(
            models.Q(first_name__icontains=search_term) |
            models.Q(middle_name__icontains=search_term) |
            models.Q(last_name__icontains=search_term) |
            models.Q(mobile_own__icontains=search_term)
        )[:10]
        
        students_data = []
        for admission in admissions:
            remaining = admission.total_fees - admission.paid_fees
            students_data.append({
                'id': admission.id,
                'full_name': admission.get_full_name(),
                'course': admission.course_name,
                'batch': admission.batch,
                'mobile': admission.mobile_own,
                'total_fees': float(admission.total_fees),
                'paid_fees': float(admission.paid_fees),
                'remaining_fees': float(remaining),
                'form_no': admission.form_no
            })
        
        return JsonResponse({
            'success': True,
            'students': students_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def payment_history(request):
    """Payment history page with filters"""
    if 'student_id' not in request.session:
        messages.error(request, 'Please login to access this page.')
        return redirect('login')
    
    context = {
        'student_name': request.session.get('student_name')
    }
    return render(request, 'payment_history.html', context)

@csrf_exempt
def get_payment_history(request):
    """API endpoint to get filtered payment history"""
    if 'student_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        course = request.GET.get('course', '')
        batch = request.GET.get('batch', '')
        student_name = request.GET.get('student_name', '').strip().lower()
        
        # Build query
        payments = Payment.objects.select_related('admission').all()
        
        if course:
            payments = payments.filter(admission__course_name=course)
        
        if batch:
            payments = payments.filter(admission__batch=batch)
        
        if student_name:
            payments = payments.filter(
                models.Q(admission__first_name__icontains=student_name) |
                models.Q(admission__middle_name__icontains=student_name) |
                models.Q(admission__last_name__icontains=student_name)
            )
        
        # Prepare data
        payments_data = []
        for payment in payments:
            payments_data.append({
                'id': payment.id,
                'receipt_no': payment.receipt_no,
                'payment_date': payment.payment_date.strftime('%Y-%m-%d'),
                'student_name': payment.admission.get_full_name(),
                'form_no': payment.admission.form_no,
                'course': payment.admission.course_name,
                'batch': payment.admission.batch,
                'mobile': payment.admission.mobile_own,
                'amount_paid': float(payment.amount_paid),
                'payment_mode': payment.payment_mode,
                'transaction_ref': payment.transaction_ref or '',
                'remarks': payment.remarks or '',
                'created_by': payment.created_by or 'Admin'
            })
        
        return JsonResponse({
            'success': True,
            'payments': payments_data,
            'count': len(payments_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_receipt_details(request):
    """API endpoint to get receipt details for printing"""
    if 'student_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        receipt_no = request.GET.get('receipt_no', '')
        
        if not receipt_no:
            return JsonResponse({'error': 'Receipt number required'}, status=400)
        
        payment = Payment.objects.select_related('admission').get(receipt_no=receipt_no)
        
        receipt_data = {
            'receipt_no': payment.receipt_no,
            'payment_date': payment.payment_date.strftime('%d/%m/%Y'),
            'student_name': payment.admission.get_full_name(),
            'course': payment.admission.course_name,
            'batch': payment.admission.batch,
            'amount_paid': float(payment.amount_paid),
            'amount_in_words': payment.get_amount_in_words(),
            'payment_mode': payment.get_payment_mode_display(),
            'transaction_ref': payment.transaction_ref or ''
        }
        
        return JsonResponse({
            'success': True,
            'receipt': receipt_data
        })
        
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Receipt not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def export_payment_history(request):
    """Export filtered payment history to Excel"""
    if 'student_id' not in request.session:
        return redirect('login')
    
    import openpyxl
    from django.http import HttpResponse
    
    try:
        course = request.GET.get('course', '')
        batch = request.GET.get('batch', '')
        student_name = request.GET.get('student_name', '').strip().lower()
        
        # Build query
        payments = Payment.objects.select_related('admission').all()
        
        if course:
            payments = payments.filter(admission__course_name=course)
        
        if batch:
            payments = payments.filter(admission__batch=batch)
        
        if student_name:
            payments = payments.filter(
                models.Q(admission__first_name__icontains=student_name) |
                models.Q(admission__middle_name__icontains=student_name) |
                models.Q(admission__last_name__icontains=student_name)
            )
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Payment History"
        
        # Headers
        headers = [
            'Receipt No', 'Payment Date', 'Student Name', 'Form No',
            'Course', 'Batch', 'Mobile', 'Amount Paid',
            'Payment Mode', 'Transaction Ref', 'Created By'
        ]
        
        # Write headers
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
            cell.fill = openpyxl.styles.PatternFill(
                start_color="4472C4",
                end_color="4472C4",
                fill_type="solid"
            )
        
        # Write data
        for row, payment in enumerate(payments, 2):
            ws.cell(row=row, column=1, value=payment.receipt_no)
            ws.cell(row=row, column=2, value=payment.payment_date.strftime('%d/%m/%Y'))
            ws.cell(row=row, column=3, value=payment.admission.get_full_name())
            ws.cell(row=row, column=4, value=payment.admission.form_no)
            ws.cell(row=row, column=5, value=payment.admission.course_name)
            ws.cell(row=row, column=6, value=payment.admission.batch)
            ws.cell(row=row, column=7, value=payment.admission.mobile_own)
            ws.cell(row=row, column=8, value=float(payment.amount_paid))
            ws.cell(row=row, column=9, value=payment.get_payment_mode_display())
            ws.cell(row=row, column=10, value=payment.transaction_ref or 'N/A')
            ws.cell(row=row, column=11, value=payment.created_by or 'N/A')
        
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
        filename = f"payment_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Save workbook
        wb.save(response)
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting data: {str(e)}')
        return redirect('payment_history')