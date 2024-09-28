from django.contrib import admin
from .models import Offer
from .forms import OfferForm

class OfferAdmin(admin.ModelAdmin):
    form = OfferForm
    list_display = ['offer_type', 'category', 'product', 'percentage', 'valid_from', 'valid_to', 'is_active']
    list_filter = ['offer_type', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['offer_type', 'category__name', 'product__name']

admin.site.register(Offer, OfferAdmin)
