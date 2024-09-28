from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('resend-otp/', views.resend_otp, name='resend-otp'),
    #Optionally, if you have custom routes for social authentication
    #path('google-authenticate/', views.google_authenticate, name='google_authenticate'),  # New URL
    #path('google-authenticate/', views.test_google_authenticate, name='test_google_authenticate'),
    path('google-authenticate/', views.google_authenticate, name='google_authenticate'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('',views.dashboard,name='dashboard'),
    path('forgotpassword/',views.forgotpassword,name="forgotpassword"),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetpassword/', views.resetpassword, name='resetpassword'),
    path('my_orders/',views.my_orders,name='my_orders'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),

    path('change_password/',views.change_password,name='change_password'),
    path('order_details/<int:order_id>/',views.order_details,name='order_details'),
    path('address/',views.address,name='address'),
    path('add_address/',views.add_address,name='add_address'),
    path('edit_address/<int:address_id>/',views.edit_address,name='edit_address'),
    path('delete_address/<int:address_id>/',views.delete_address,name='delete_address'),

    path('change_address/',views.change_address,name='change_address'),
    path('select_address/<int:address_id>/', views.select_address, name='select_address'),



]


