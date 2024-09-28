from django.shortcuts import render,redirect,get_object_or_404
from .models import Offer
from django.contrib import messages
from .forms import OfferForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test


@user_passes_test(lambda u:u.is_superadmin,login_url="admin_login")
def offer_view(request):
    offers = Offer.objects.all()
    paginator = Paginator(offers, 10)  # Show 10 offers per page
    page_number = request.GET.get('page')
    offers = paginator.get_page(page_number)
    
    context = {
        'offers': offers
    }
    return render(request, 'cadmin/offer_list.html', context)

@user_passes_test(lambda u:u.is_superadmin,login_url="admin_login")
def add_offer(request):
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offer added successfully!')
            return redirect('offer_view')  # Replace with the appropriate URL name for your offer list view
    else:
        form = OfferForm()

    return render(request, 'cadmin/add_offer.html', {'form': form})    
@user_passes_test(lambda u:u.is_superadmin,login_url="admin_login")
def edit_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    
    if request.method == 'POST':
        form = OfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offer updated successfully!')
            return redirect('offer_view')  # Replace with the appropriate URL name for your offer list view
    else:
        form = OfferForm(instance=offer)

    return render(request, 'cadmin/edit_offer.html', {'form': form, 'offer': offer})    
@user_passes_test(lambda u:u.is_superadmin,login_url="admin_login")
def toggle_offer_status(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    offer.is_active = not offer.is_active
    offer.save()
    status = 'activated' if offer.is_active else 'deactivated'
    messages.success(request, f'Offer {status} successfully!')
    return redirect('offer_view')     