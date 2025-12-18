from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # LOGIN / LOGOUT
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='login.html'),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='home'),
        name='logout'
    ),

    # ✅ PASSWORD RESET (THIS FIXES YOUR ERROR)
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html'
        ),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ),
        name='password_reset_done'
    ),
]
