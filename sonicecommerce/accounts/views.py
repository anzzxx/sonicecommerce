import json
import random
import datetime
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render, redirect,get_object_or_404
from .forms import RegistrationForm,UserForm,UserProfileForm,AddressForm
from .models import Accounts,UserProfile,Address
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .utils import send_otp, format_phone_number
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth
#email
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from orders.models import OrderRequest
from carts.views import _cart_id
from carts.models import Cart,CartItem

import requests
from orders.models import *
from wallet.models import Wallet


import logging

def register(request):
    """
    Handles user registration.

    If the request method is POST, this function processes the registration form,
    validates the data, creates a new user, generates an OTP, and sends it to the user's phone number.
    If the phone number is already in use, it shows an error message.

    On successful registration, it redirects the user to the OTP verification page.
    If the request method is GET, it renders the registration form.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the registration form or redirects to the OTP verification page.
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Extract cleaned data from the form
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            
            # Format phone number
            phone_number = format_phone_number(phone_number)
            
            # Check if phone number already exists
            if Accounts.objects.filter(phone_number=phone_number).exists():
                messages.error(request, "This phone number is already in use.")
                return render(request, 'account/register.html', {'form': form})
                
            # Create a new user
            user = Accounts.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            
            # Set additional user attributes
            user.phone_number = phone_number
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.otp_expiration = datetime.datetime.now() + datetime.timedelta(minutes=10)  # OTP valid for 10 minutes
            user.save()
            
            # Create or get user profile
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.save()
            
            # Create wallet for the user
            wallet = Wallet.objects.create(user=user)
            wallet.save()

            # Send OTP to the user's phone number
            send_otp(phone_number, otp)
            
            # Store phone number in session
            request.session['phone_number'] = phone_number

            # Redirect to OTP verification page
            return redirect('/accounts/verify-otp/')
    
    else:
        form = RegistrationForm()

    # Render registration form
    context = {
        'form': form
    }
    return render(request, 'account/register.html', context)



def verify_otp(request):
    """
    Verifies the OTP entered by the user.

    This function checks if the provided OTP matches the one stored for the user
    and if it is still valid. If valid, it activates the user's account; otherwise,
    it shows an error message and redirects the user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the OTP verification page or redirects to login page.
    """
    phone_number = request.session.get('phone_number')

    if request.method == 'POST':
        otp = request.POST.get('otp')

        if not phone_number:
            messages.error(request, 'Phone number is not available')
            return redirect('register')

        if otp:
            users = Accounts.objects.filter(phone_number=phone_number)

            if users.exists():
                user = users.first()
                if user.otp == otp and user.otp_expiration > timezone.now():
                    user.is_active = True
                    user.otp = ''
                    user.otp_expiration = None
                    user.save()
                    del request.session['phone_number']
                    messages.success(request, 'Your account has been activated')
                    return redirect('login')
                else:
                    messages.error(request, 'Invalid or expired OTP')
                    return redirect('verify_otp')
            else:
                messages.error(request, 'Invalid phone number')
                return redirect('verify_otp')

    return render(request, 'account/verify_otp.html')



def resend_otp(request):
    """
    Resends the OTP to the user's phone number.

    This function generates a new OTP and updates the user's record with the new OTP
    and its expiration time. It then sends the OTP to the user. If the OTP is sent successfully,
    it redirects to the login page; otherwise, it shows an error message.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to login page or registration page based on success or failure.
    """
    if request.method == 'POST':
        phone_number = request.session.get('phone_number')
        if not phone_number:
            messages.error(request, 'Invalid phone number.')
            return redirect('register')

        try:
            user = Accounts.objects.get(phone_number=phone_number)
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.otp_expiration = timezone.now() + datetime.timedelta(minutes=10)  # OTP valid for 10 minutes
            user.save()

            # Send OTP
            if send_otp(phone_number, otp):
                messages.success(request, 'OTP resent successfully.')
                return redirect('login')
            else:
                messages.error(request, 'Failed to send OTP. Please try again.')
                return redirect('verify_otp')
        
        except Accounts.DoesNotExist:
            messages.error(request, 'Account does not exist.')
            return redirect('register')

    else:
        messages.error(request, 'Invalid request method.')
        return redirect('register')



def login(request):
    """
    Handles user login.

    Authenticates the user with the provided email and password. If successful, the function
    attempts to restore the user's cart items from a previous session and associates them with
    the logged-in user. If there is a 'next' parameter in the URL query string, it redirects
    the user to that page; otherwise, it redirects to the dashboard.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the login page or redirects to a specified page based on the success
                      or failure of the login process.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user
        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            try:
                # Attempt to restore the cart for the user
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exists:
                    cart_items = CartItem.objects.filter(cart=cart)
                    product_variation = [list(item.variation.all()) for item in cart_items]

                    # Get existing cart items for the user
                    user_cart_items = CartItem.objects.filter(user=user)
                    existing_variations = [list(item.variation.all()) for item in user_cart_items]
                    item_ids = [item.id for item in user_cart_items]

                    # Update quantities for matching variations
                    for variations in product_variation:
                        if variations in existing_variations:
                            index = existing_variations.index(variations)
                            item_id = item_ids[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            # Assign the cart items to the user
                            for item in cart_items:
                                item.user = user
                                item.save()

            except Cart.DoesNotExist:
                # Handle case where cart does not exist
                pass

            # Log the user in
            auth.login(request, user)
            messages.success(request, 'Login successful')

            # Redirect to the next page or dashboard
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
            except Exception:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'account/login.html')



@login_required(login_url='login')
def logout(request):
    """
    Logs out the user.

    This function logs out the current user, displays a success message,
    and redirects the user to the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to the login page after logging out.
    """
    auth.logout(request)
    messages.success(request, 'You are logged out')
    return redirect('login')



def activate(request, uidb64, token):
    """
    Activates a user account based on the activation link.

    This function decodes the user ID and checks the token to verify
    and activate the user account. If successful, it redirects the user
    to the login page. If the activation link is invalid, it redirects
    to the registration page with an error message.

    Args:
        request (HttpRequest): The HTTP request object.
        uidb64 (str): Base64 encoded user ID.
        token (str): Activation token.

    Returns:
        HttpResponse: Redirects to the login page on success or the
                      registration page on failure.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Accounts._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Accounts.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')



# Initialize logger
logger = logging.getLogger(__name__)

def google_authenticate(request):
    """
    Handles Google authentication for a user.

    If the user is authenticated and has associated Google social authentication,
    it updates the user's profile with Google account data. Redirects to the user's
    profile page upon successful update or to an error page if social authentication
    data is missing.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to the profile page or error page based on success or failure.
    """
    if request.user.is_authenticated:
        user = request.user
        try:
            social_auth = UserSocialAuth.objects.get(user=user, provider='google')
            google_data = social_auth.extra_data
        except UserSocialAuth.DoesNotExist:
            logger.error("UserSocialAuth does not exist for user: %s", user)
            return redirect('/error')

        email = google_data.get('email')
        name = google_data.get('name', '')

        if name:
            name_parts = name.split()
            user.first_name = name_parts[0]
            user.last_name = ' '.join(name_parts[1:])
        if email:
            user.email = email
        
        user.is_active = True
        user.save()

        return redirect('/profile')
    else:
        return redirect('/login')


@login_required(login_url='login')
def dashboard(request):
    """
    Renders the user dashboard.

    Retrieves the user's orders and profile information. Displays the total number of
    orders and the user's profile picture if available.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the dashboard page with context including orders count,
                      user profile, and profile picture.
    """
    # Retrieve the user's orders
    orders = Order.objects.filter(user_id=request.user.id, is_orderd=True).order_by('-created_at')
    orders_count = orders.count()

    # Retrieve the user profile
    try:
        userprofile = UserProfile.objects.get(user_id=request.user.id)
        profile_picture = userprofile.profile_picture.url if userprofile.profile_picture else ''
    except UserProfile.DoesNotExist:
        userprofile = None
        profile_picture = 'No profile'  # Default to an empty string if the profile or picture doesn't exist

    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
        'profile_picture': profile_picture,  # Add profile picture to the context
    }

    return render(request, 'account/dashboard.html', context)



def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Accounts.objects.filter(email=email).exists():
            user = Accounts.objects.get(email__exact=email)

            current_site = get_current_site(request)
            print(f'current{current_site}')
            current_site = '127.0.0.1:8000'
            mail_subject = 'Reset Your Password'
            message = render_to_string('account/reset_password_email.html', {
                'user': user,
                'domain': current_site,  # Pass the domain attribute
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            try:
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()
                messages.success(request, 'Password reset email has been sent.')
            except Exception as e:
                messages.error(request, f'An error occurred while sending the email: {e}')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist.')
            return redirect('forgotpassword')

    return render(request, 'account/forgotpassword.html')

    

    return render(request,'account/forgotpassword.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        #user=Accounts.default_manager.get(pk=uid)
        user = Accounts.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Accounts.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request,'Reset your password ')
        return redirect('resetpassword')
    else:
        messages.error(request,'This link is expires')
        return redirect('login')    


     

def resetpassword(request):
    if request.method=='POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']

        if password==confirm_password:
            uid=request.session.get('uid')
            user=Accounts.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset succesfully')
            return redirect('login')

        else:
            messages.error(request,'password do not match')
            return redirect('resetpassword')
    else:

        return render(request,'account/resetpassword.html')

        
@login_required(login_url='login')        
def my_orders(request):
    orders=Order.objects.filter(user=request.user,is_orderd=True).order_by('-created_at')
    context={
        'orders':orders,
    }
    return render(request,'account/my_orders.html',context)
    
@login_required(login_url='login')
def edit_profile(request):
    #print(request.user)
    userprofile=get_object_or_404(UserProfile,user=request.user)
    if request.method=="POST":
        #print('insaide post')
        user_form=UserForm(request.POST,instance=request.user)
        profile_form=UserProfileForm(request.POST,request.FILES,instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Your profile has been updated')
            return redirect('edit_profile')
    else:
        user_form=UserForm(instance=request.user)
        profile_form=UserProfileForm(instance=userprofile) 
    context={
            'user_form':user_form,
            'profile_form':profile_form,
            'userprofile':userprofile,
    }       
    return render(request,'account/edit_profile.html',context)
@login_required(login_url='login')
def change_password(request):
    if request.method=='POST':
        current_password=request.POST['current_password']
        new_password=request.POST['new_password']
        confirm_password=request.POST['confirm_password']

        user=Accounts.objects.get(username__exact=request.user.username)
        if new_password==confirm_password:
            success=user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                #auth.logout(request)

                messages.success(request,'Password updates successfully')
                return redirect('change_password')
            else:
                messages.error(request,'please enter valid password')    
        else:
            messages.error(request,'password does not match')
            return redirect('change_password')
    return render(request,'account/change_password.html')

@login_required(login_url='login')
def order_details(request, order_id):
    """
    Display the details of a specific order, including order products,
    subtotal, and request status if applicable.

    Args:
        request: The HTTP request object.
        order_id: The order number to retrieve details for.

    Returns:
        Renders the 'order_detail.html' template with order details and context.
    """
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    request_exist = OrderRequest.objects.filter(order=order).exists()
    request_status = OrderRequest.objects.filter(order=order).first()
    
    sub_total = 0
    for i in order_detail:
        sub_total += i.product_price * i.quantity
    
    context = {
        'order_detail': order_detail,
        'order': order,
        'sub_total': sub_total,
        'request_exist': request_exist,
        'request_status': request_status
    }
    return render(request, 'account/order_detail.html', context)

@login_required
def address(request):
    """
    Display a list of addresses associated with the user's profile.

    Args:
        request: The HTTP request object.

    Returns:
        Renders the 'address.html' template with the user's address list.
    """
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        address_list = Address.objects.filter(user_profile=user_profile)
    except UserProfile.DoesNotExist:
        address_list = []
    
    context = {
        'address': address_list
    }
    return render(request, 'account/address.html', context)

def add_address(request):
    """
    Handle the addition of a new address. If POST method, validate and save
    the address, setting it as the primary address. If GET, render the form.

    Args:
        request: The HTTP request object.

    Returns:
        Redirects to the 'next' URL or the address list page if successful,
        or renders the 'add_address.html' form if unsuccessful.
    """
    next_url = request.GET.get('next', reverse('address'))

    if request.method == "POST":
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user_profile = request.user.userprofile
            Address.objects.filter(user_profile=address.user_profile).update(is_primary=False)
            address.is_primary = True
            address.save()
            messages.success(request, 'New address added successfully!')
            return redirect(next_url)
    else:
        address_form = AddressForm()

    context = {
        'address_form': address_form,
    }
    return render(request, 'account/add_address.html', context)

def edit_address(request, address_id):
    """
    Handle the editing of an existing address.

    Args:
        request: The HTTP request object.
        address_id: The ID of the address to be edited.

    Returns:
        Redirects to the address list if successful, or renders the 
        'edit_address.html' form if unsuccessful.
    """
    address = get_object_or_404(Address, id=address_id)

    if request.method == "POST":
        address_form = AddressForm(request.POST, instance=address)
        if address_form.is_valid():
            address_form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('address')
    else:
        address_form = AddressForm(instance=address)

    context = {
        'address_form': address_form,
        'address': address,
    }
    return render(request, 'account/edit_address.html', context)

def delete_address(request, address_id):
    """
    Handle the deletion of an existing address.

    Args:
        request: The HTTP request object.
        address_id: The ID of the address to be deleted.

    Returns:
        Redirects to the address list after successful deletion, or renders 
        the 'delete_address.html' template if confirmation is required.
    """
    address = get_object_or_404(Address, id=address_id)
    
    if request.method == "POST":
        address.delete()
        messages.success(request, 'Address deleted successfully!')
        return redirect('address')

    return render(request, 'account/delete_address.html', {'address': address})

@login_required
def change_address(request):
    """
    Display a list of addresses for the user to change their current address.

    Args:
        request: The HTTP request object.

    Returns:
        Renders the 'change_address.html' template with the list of addresses.
    """
    user = request.user
    address = Address.objects.filter(user_profile=user.userprofile)

    context = {
        'address': address,
    }
    return render(request, 'account/change_address.html', context)

def select_address(request, address_id):
    """
    Set a selected address as the primary address for the user.

    Args:
        request: The HTTP request object.
        address_id: The ID of the address to be set as primary.

    Returns:
        Redirects to the 'checkout' page after updating the primary address.
    """
    selected_address = get_object_or_404(Address, id=address_id)
    selected_address.is_primary = True
    selected_address.save()

    Address.objects.exclude(id=address_id).update(is_primary=False)

    return redirect('checkout')