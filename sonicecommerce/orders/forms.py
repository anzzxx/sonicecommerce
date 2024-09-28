from django import forms
from .models import Order
from .models import OrderRequest

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order  # Corrected from 'models' to 'model'
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'postal_code']

        
class OrderRequestForm(forms.ModelForm):
    class Meta:
        model = OrderRequest
        fields = ['request_type', 'reason']

        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control'}),
        }