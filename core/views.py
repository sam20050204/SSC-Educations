from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, models
from django.db.models import Q, Count
from datetime import datetime
from decimal import Decimal
import json
import openpyxl

from .models import Student, Enquiry, Admission, Payment, Bill, BillItem

# ==================== HOME ====================

def home(request):
    return render(request, "home.html")


# ==================== LOGIN / LOGOUT ====================

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# ==================== DASHBOARD ====================

@login_required
def dashboard(request):
    selected_year = int(request.GET.get("year", datetime.now().year))

    admissions = Admission.objects.filter(
        admission_date__year=selected_year,
        is_active=True
    )

    context = {
        "total_students": admissions.count(),
        "mscit_count": admissions.filter(course_name="MS-CIT").count(),
        "klic_count": admissions.exclude(course_name="MS-CIT").count(),
        "selected_year": selected_year,
        "available_years": range(datetime.now().year, datetime.now().year - 5, -1),
    }

    return render(request, "dashboard.html", context)


# ==================== ENQUIRY ====================

@login_required
def new_enquiry(request):
    if request.method == "POST":
        Enquiry.objects.create(
            student_name=request.POST.get("student_name"),
            mobile_no=request.POST.get("mobile_no"),
            course=request.POST.get("course"),
            address=request.POST.get("address"),
        )
        messages.success(request, "Enquiry created successfully")
        return redirect("enquiry_data")

    return render(request, "new_enquiry.html")


@login_required
def enquiry_data(request):
    enquiries = Enquiry.objects.all().order_by("-created_at")
    return render(request, "enquiry_data.html", {"enquiries": enquiries})


# ==================== API EXAMPLE ====================

@csrf_exempt
@login_required
def get_admitted_students(request):
    students = Admission.objects.filter(is_active=True)
    data = [{"name": s.get_full_name(), "course": s.course_name} for s in students]
    return JsonResponse({"students": data})
