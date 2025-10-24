# Update backend/urls.py - Add these new URL patterns

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
    path("new-admission/", views.new_admission, name="new_admission"),
    path("fees-payment/", views.fees_payment, name="fees_payment"),
    path("payment-history/", views.payment_history, name="payment_history"),
    path("students-details/", views.students_details, name="students_details"),
    path("admitted-students/", views.admitted_students, name="admitted_students"),
    
    # API Endpoints
    path("api/get-admitted-students/", views.get_admitted_students, name="get_admitted_students"),
    path("api/update-student/", views.update_student, name="update_student"),
    path("api/search-student-payment/", views.search_student_for_payment, name="search_student_payment"),
    path("api/get-payment-history/", views.get_payment_history, name="get_payment_history"),
    path("api/get-receipt/", views.get_receipt_details, name="get_receipt_details"),
    
    # Export Endpoints
    path("export-payment-history/", views.export_payment_history, name="export_payment_history"),
# In urlpatterns list, add:
    path("api/delete-student-admission/", views.delete_student_admission, name="delete_student_admission"),]
    path("new-bill/", views.new_bill, name="new_bill"),
    path("bills/", views.bills_list, name="bills_list"),
    path("print-bill/<int:bill_id>/", views.print_bill, name="print_bill"),
    path("api/get-bills/", views.get_bills, name="get_bills"),
    path("export-bills/", views.export_bills, name="export_bills"),

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)