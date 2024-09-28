from django import forms
from .models import Accounts,UserProfile,Address

class RegistrationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter password'
    }))

    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'confirm password'
     }))
    
    class Meta:
        model = Accounts
        fields = ["first_name","last_name","phone_number","email","password"]
    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder']='Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder']='Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder']='Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder']='Enter Email'
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'


    def  clean(self):
        cleaned_data= super(RegistrationForm,self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')  

        if password != confirm_password:
            raise forms.ValidationError(
                'password does not match!'
            )  
class UserEditForm(forms.ModelForm):
    class Meta:
        model = Accounts
        fields = ['first_name', 'last_name', 'phone_number', 'email','username','is_active','is_staff','is_superadmin','is_admin']
    
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'        

class UserForm(forms.ModelForm):
    class Meta:
        model=Accounts
        fields=('first_name','last_name','phone_number')
    def __init__(self,*args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control' 

class UserProfileForm(forms.ModelForm):

    profile_picture = forms.ImageField(
        required=False, 
        error_messages={'invalid': ("Image file only")},
        widget=forms.FileInput
    )
    
    class Meta:
        model = UserProfile
        fields = ('profile_picture',)  # Correctly defined as a tuple with a trailing comma
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'country', 'postal_code','phone_primary','phone_secondery']
        
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'