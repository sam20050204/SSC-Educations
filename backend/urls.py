from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("new-enquiry/", views.new_enquiry, name="new_enquiry"),
    path("enquiry-data/", views.enquiry_data, name="enquiry_data"),
    path("export-enquiries/", views.export_enquiries, name="export_enquiries"),
    path("new-admission/", views.new_admission, name="new_admission"),  # Updated
    path("fees-payment/", views.fees_payment, name="fees_payment"),
    path("students-details/", views.students_details, name="students_details"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)