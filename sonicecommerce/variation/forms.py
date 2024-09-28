from django import forms
from .models import Variation

class VariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = ['product', 'variation_category', 'variation_value', 'quantity', 'price','defult', 'is_active']

        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'variation_category': forms.Select(attrs={'class': 'form-control'}),
            'variation_value': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'defult': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
