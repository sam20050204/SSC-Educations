from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from students.views import role_login_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('students.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

urlpatterns += [
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html'
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),
]


path('login-redirect/', role_login_redirect),
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # ✅ ADD THESE LINES
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html'
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),
]
