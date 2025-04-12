from django.urls import path

from apps.users import views

urlpatterns = [
    path('admin-portal/login/', views.admin_login),
]