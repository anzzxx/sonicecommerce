
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.urls import reverse
from .models import Coupon
from django.contrib import messages
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '')
        redirect_url = request.META.get('HTTP_REFERER')  # Get the current page URL to redirect back

        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            request.session['coupon_id'] = coupon.id
            request.session['discount_amount'] = str(coupon.discount_amount)
            messages.success(request, 'Coupon applied successfully!')
            
            # Clear the coupon session data right after applying
          
            
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid or expired coupon code.')
        
        return HttpResponseRedirect(redirect_url)