# myapp/pipeline.py
from .models import UserProfile
def activate_user(strategy, details, response, *args, **kwargs):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = kwargs.get('user')

    if user:
        # Ensure user is active after authentication
        user.is_active = True
        user.save()
        
       

        return {'user': user}
