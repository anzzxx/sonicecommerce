from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from store.models import Product
from variation.models import Variation
from carts.models import Cart, CartItem
from .models import Wishlist
from django.http import HttpResponseRedirect

@login_required(login_url='login')
def add_wishlist(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)

    if request.method == 'POST':
        selected_color = request.POST.get('selected')  # Get selected color/variation from the form

        # Fetch the selected variation based on the color
        if selected_color:
            try:
                product_var = Variation.objects.get(product=product, variation_value=selected_color)
            except Variation.DoesNotExist:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            # Get default variation if no color is selected
            try:
                product_var = Variation.objects.get(product=product, defult=True)
            except Variation.DoesNotExist:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Check if the wishlist item with the same product and variation already exists
        wishlist_item_exists = Wishlist.objects.filter(
            user=request.user, 
            product=product,
            variations=product_var
        ).exists()

        if wishlist_item_exists:
            pass
        else:
            # Create a new wishlist entry with the selected variation
            wishlist_item = Wishlist.objects.create(
                user=request.user, 
                product=product
            )
            wishlist_item.variations.add(product_var)  # Add the variation
            wishlist_item.save()
            return redirect('wishlist')

    # Redirect to the same page or previous page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='login')
def remove_from_wishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id)
    wishlist_item.delete()
    return redirect('wishlist')

@login_required(login_url='login')
def wishlist(request):
    if request.method == 'POST':
        wishlist_item_id = request.POST.get('wishlist_item_id')
        if wishlist_item_id:
            wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id)
            wishlist_item.delete()
            return redirect('wishlist')

    # Get all wishlist items for the current user
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    # For each wishlist item, fetch the corresponding variation and assign its price
    for item in wishlist_items:
        variations = item.variations.all()  # Get the variations linked to this wishlist item
        if variations.exists():
            # Assuming there's only one variation per wishlist item
            selected_variation = variations.first()  # Get the first variation (since it's a ManyToMany field)
            item.product_price = selected_variation.price# Attach the variation price to the item
            item.variation_val= selected_variation.variation_value 
        else:
            # Fallback to the product price if no variation is found
            item.product_price = item.product.price  
        
    # Create a set of product slugs that are in the user's wishlist
    wishlist_product_slugs = set(wishlist_items.values_list('product__slug', flat=True))
    
    context = {
        'wishlist_items': wishlist_items,
        'wishlist_product_slugs': wishlist_product_slugs,
    }

    return render(request, 'wishlist/wishlist.html', context)


