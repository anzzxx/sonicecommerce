from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver
from .models import Accounts

@receiver(social_account_added)
def handle_social_account(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    extra_data = sociallogin.account.extra_data
    google_id = extra_data.get('sub')
    picture = extra_data.get('picture')
    
    if not user.is_active:
        user.is_active = True
        user.save()

    if google_id:
        user.google_id = google_id
    if picture:
        user.picture = picture
    user.save()
