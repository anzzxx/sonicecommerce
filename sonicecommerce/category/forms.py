from django import forms
from .models import Category
from django.core.exceptions import ValidationError
class CategoryForm(forms.ModelForm):
    cat_image=forms.ImageField(required=False, error_messages={'invalid':("Image file only")},widget=forms.FileInput)
    class Meta:
        model = Category
        fields = ['category_name','slug','description','cat_image']
    
    def clean_category_name(self):
        category_name = self.cleaned_data.get('category_name')
        if not category_name:
            raise ValidationError('This field is required.')
        if not category_name.isalnum():
            raise ValidationError('Product name should contain only letters and numbers.')
        if len(category_name) < 3 or len(category_name) > 50:
            raise ValidationError('Product name must be between 3 and 50 characters.')
        return category_name    

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'                       

   