from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),        # Home page
    path("register/", views.register, name="register"),  # Register page
    path("login/", views.login_view, name="login"),  # Add this line

]
