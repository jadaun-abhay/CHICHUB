from django.urls import path

from apps.users import views

urlpatterns = [
    path('admin-portal/login/', views.admin_login),
    path('register/', views.user_register),
    path('login/', views.user_login),
    path('logout/', views.user_logout),
]