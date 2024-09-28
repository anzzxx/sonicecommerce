from django.urls import path
from . import views

urlpatterns = [
   path('place_order/',views.place_order,name="place_order"),
   path('payments/',views.payments,name="payments"), 
   path('cod-payment/',views.cod_payment, name='cod_payment'),
   path('wallet_payment/<int:id>/',views.wallet_payment, name='wallet_payment'),
   path('order_complete/', views.order_complete, name='order_complete'),

   path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
   path('return_order/<int:order_id>/', views.return_order, name='return_order'),
   path('download-invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
   path('invoice/<int:order_id>/', views.invoice, name='invoice'),

   path('order/<int:order_id>/request/', views.request_cancel_or_return, name='request_cancel_or_return'),
   path('payment_failed/',views.payment_failed,name="payment_failed")

   
]

