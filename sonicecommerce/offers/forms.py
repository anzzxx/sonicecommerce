from django import forms
from .models import Offer
# from store.models import Product  # You can comment this out for now

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = '__all__'
        # 'product': ProductSelectWidget(attrs={'class': 'form-control'}),
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['product'].widget.choices = [(p.id, p.product_name) for p in Product.objects.all()]
