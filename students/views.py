from django.shortcuts import render, redirect
from .models import Enquiry
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

def home(request):
    if request.method == "POST":
        Enquiry.objects.create(
            name=request.POST.get("name"),
            mobile=request.POST.get("mobile"),
            education=request.POST.get("education"),  # ✅ NEW
            course=request.POST.get("course")
        )
        return redirect("home")

    return render(request, "home.html")


def role_login_redirect(request, user):
    if user.is_superuser:
        return redirect('/admin/')
    elif user.is_staff:
        return redirect('/staff-dashboard/')
    else:
        return redirect('/')
