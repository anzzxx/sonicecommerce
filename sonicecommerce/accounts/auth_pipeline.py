# myapp/auth_pipeline.py
from .models import UserProfile
from wallet.models import Wallet

def activate_user(request, sociallogin, user, **kwargs):
    # Set user as active
    user.is_active = True
    user.save()
    user=user
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    user_profile.user = user
    user_profile.save()
    wallet=Wallet.objects.create(user=user)
    wallet.save()
    
    
    #user_profile, created = UserProfile.objects.get_or_create(user=user)
