from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),        # Home page
    path("register/", views.register, name="register"),  # Register page
    path("login/", views.login_view, name="login"),  # Login page
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("dashboard/", views.dashboard, name="dashboard"),  # Dashboard page
    path("logout/", views.logout_view, name="logout"),  # Logout
    path("new-enquiry/", views.new_enquiry, name="new_enquiry"),  # New Enquiry
    path("enquiry-data/", views.enquiry_data, name="enquiry_data"),  # Enquiry Data View
    path("export-enquiries/", views.export_enquiries, name="export_enquiries"),  # Export to Excel
    path("new-admission/", views.new_admission, name="new_admission"),  # New Admission
    path("fees-payment/", views.fees_payment, name="fees_payment"),  # Fees Payment
    path("students-details/", views.students_details, name="students_details"),  # Students Details
]