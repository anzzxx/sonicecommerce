from django import forms
from .models import Coupon
from datetime import datetime

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_amount', 'valid_from', 'valid_to', 'is_active']
        widgets = {
            'valid_from': forms.DateInput(attrs={'type': 'text', 'class': 'datepicker', 'placeholder': 'YYYY-MM-DD'}),
            'valid_to': forms.DateInput(attrs={'type': 'text', 'class': 'datepicker', 'placeholder': 'YYYY-MM-DD'}),
        }

    def clean_valid_from(self):
        date = self.cleaned_data.get('valid_from')
        if date and date < datetime.today().date():
            raise forms.ValidationError("The start date cannot be in the past.")
        return date

    def clean_valid_to(self):
        date = self.cleaned_data.get('valid_to')
        valid_from = self.cleaned_data.get('valid_from')
        if date and (valid_from and date < valid_from):
            raise forms.ValidationError("The end date cannot be before the start date.")
        return date
