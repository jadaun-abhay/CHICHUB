from django.urls import path

from apps.warehouse import views

urlpatterns = [
    path('warehouse/categories/', views.category_management),
    path('warehouse/categories/<str:category_id>/', views.category_management),
]