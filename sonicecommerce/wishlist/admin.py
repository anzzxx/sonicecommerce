from django.contrib import admin
from .models import Wishlist  # Import the Wishlist model
# Register your models here.


class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_date')  # Fields to display in the admin list view
    search_fields = ('user__username', 'product__product_name')  # Enable search by user and product
    list_filter = ('added_date',)  # Add filter for added_date
    filter_horizontal = ('variations',)  # For better UI to handle ManyToManyField

# Register the Wishlist model with the admin
admin.site.register(Wishlist, WishlistAdmin)
