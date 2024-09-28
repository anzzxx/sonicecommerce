from django.urls import path
from . import views

urlpatterns = [
    path('add_wishlist/<slug:product_slug>/', views.add_wishlist, name='add_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('remove_from_wishlist/<int:wishlist_item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]