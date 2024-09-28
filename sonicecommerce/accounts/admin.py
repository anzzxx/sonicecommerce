from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . models import Accounts,UserProfile,Address
from django.utils.html import format_html
# Register your models here.

class AccountAdmin(UserAdmin):
    list_display=('email','first_name','last_name','username','last_login','date_joined','is_active')
    
    list_display_links=('email','first_name','last_name')
    readonly_fields=('last_login','date_joined')
    ordering=('date_joined',)
    filter_horizontal=()
    list_filter=()
    fieldsets=()

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        if object.profile_picture:  # Check if the profile picture exists
            return format_html('<img src="{}" width="30" style="border-radius:50%;">', object.profile_picture.url)
        else:
            return format_html('<img src="{}" width="30" style="border-radius:50%;">', '/static/images/profile.jpeg')
            #Replace '/static/images/default-profile.png' with the actual path to your default image
    
    thumbnail.short_description = 'Profile Picture'
    
    #list_display = ('thumbnail', 'user', 'city', 'state', 'country')

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'address_line_1', 'city', 'state', 'country', 'postal_code','phone_primary','phone_secondery']
    search_fields = ['user_profile__user__username', 'address_line_1', 'city', 'state', 'country']
    list_filter = ['country', 'state', 'city']

admin.site.register(Address, AddressAdmin)    
admin.site.register(Accounts,AccountAdmin)
admin.site.register(UserProfile,UserProfileAdmin)
