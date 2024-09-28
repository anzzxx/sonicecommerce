# myapp/adapters.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .auth_pipeline import activate_user

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Call your custom function
        activate_user(request, sociallogin, user)
        return user
