# myapp/backends.py

from social_core.backends.google import GoogleOpenIdConnect

class CustomGoogleOpenIdConnect(GoogleOpenIdConnect):
    
    def user_data(self, access_token, *args, **kwargs):
        data = super().user_data(access_token, *args, **kwargs)
        # Add any additional processing or data modifications if needed
        return data

    def user_exists(self, *args, **kwargs):
        user = super().user_exists(*args, **kwargs)
        if user:
            # Ensure user is active
            user.is_active = True
            user.save()
        return user

