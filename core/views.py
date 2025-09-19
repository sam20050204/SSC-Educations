from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import re

def home(request):
    return render(request, "home.html")

def register(request):
    error = None
    if request.method == "POST":
        name = request.POST.get("name")
        mobile = request.POST.get("mobile")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # ✅ Password match check
        if password1 != password2:
            error = "Passwords do not match."
        # ✅ Password strength check
        elif len(password1) < 8 or not re.search(r"\d", password1) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password1):
            error = "Password must be at least 8 characters, include a number and a special symbol."
        # ✅ Check if email already exists
        elif User.objects.filter(username=email).exists():
            error = "Email already registered."
        else:
            # Create new user
            user = User.objects.create(
                username=email,
                first_name=name,
                email=email,
                password=make_password(password1)
            )
            user.save()
            return redirect("home")  # After success, go to home page

    return render(request, "register.html", {"error": error})
