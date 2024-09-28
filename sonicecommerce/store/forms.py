from django import forms
import re
from .models import Product, ProductImage, ReviewRating
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class ProductForm(forms.ModelForm):
    image = forms.ImageField(required=False, error_messages={'invalid': "Image file only"}, widget=forms.FileInput)

    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'category', 'description', 'price', 'stock', 'is_available', 'image']

    price = forms.IntegerField(
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={'min': '0'})
    )
    stock = forms.IntegerField(
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={'min': '0'})
    )

    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')

        # Check if the field is empty
        if not product_name:
            raise ValidationError('This field is required.')

        # Check if the product name contains only letters, numbers, and spaces
        if not re.match(r'^[a-zA-Z0-9 ]+$', product_name):
            raise ValidationError('Product name should contain only letters, numbers, and spaces.')

        # Check the length of the product name
        if len(product_name) < 3 or len(product_name) > 50:
            raise ValidationError('Product name must be between 3 and 50 characters.')

        return product_name

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class ProductImageForm(forms.ModelForm):
    image = forms.ImageField(required=False, error_messages={'invalid': "Image file only"}, widget=forms.FileInput)

    class Meta:
        model = ProductImage
        fields = ['image']

ProductImageFormSet = forms.inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=3,  # Number of empty forms to display initially
    max_num=3,  # Maximum number of forms
    can_delete=True  # Allow deletion of images
)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'review': forms.Textarea(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5})
        }
