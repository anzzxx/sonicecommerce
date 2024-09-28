from django.urls import path
from . import views

urlpatterns = [
   path('',views.variation_view,name="variation_view"),
   path('variations/add/', views.variation_create, name='variation_create'),
   path('variations/<int:pk>/edit/', views.variation_update, name='variation_update'),
    path('variations/<int:pk>/toggle/', views.variation_toggle_status, name='variation_toggle_status'),
]