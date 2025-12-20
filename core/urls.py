from django.urls import path
from . import views

urlpatterns = [
    # ROOT PAGE
    path('', views.home, name='home'),

    # AUTH
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),
]
