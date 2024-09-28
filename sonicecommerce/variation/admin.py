from django.contrib import admin
from .models import Variation

@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ('id', 'variation_category', 'variation_value', 'price', 'quantity', 'is_active')
