from django.urls import path
from . import views

urlpatterns = [
    path('',views.offer_view,name="offer_view"),
    path('add-offer/',views.add_offer, name='add_offer'),
    path('edit-offer/<int:offer_id>/',views.edit_offer, name='edit_offer'),
    path('toggle-offer-status/<int:offer_id>/',views.toggle_offer_status, name='toggle_offer_status'),

]