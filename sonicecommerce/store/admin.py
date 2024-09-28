from django.contrib import admin
from .models import Product,ProductImage,ReviewRating
from variation.models import Variation
# Register your models here.

class ProductImageInline(admin.TabularInline):
    model=ProductImage
    extra=1

class ProductAdmin(admin.ModelAdmin):
    list_display=('product_name','price','stock','category','modified_date','is_available')
    prepopulated_fields={'slug':('product_name',)}
    inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(ReviewRating)

