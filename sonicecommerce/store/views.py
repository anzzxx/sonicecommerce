from django.shortcuts import render, get_object_or_404,redirect
from .models import Product
from category.models import Category
from .models import ProductImage,ReviewRating  # Import ProductImage here
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
from decimal import Decimal, InvalidOperation
from offers.models import Offer
from datetime import datetime, date
from .pipeline import calculate_discounted_price,get_best_offer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from variation.models import Variation



def store(request, category_slug=None):
    active_categories = Category.objects.filter(is_active=True)
    products = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = Product.objects.filter(category=category, is_available=True)
    else:
        products = Product.objects.filter(category__in=active_categories, is_available=True).order_by('id')

    # Get the best offer percentage for each product
    for product in products:
        default_variation = Variation.objects.filter(product=product, defult=True).first()
        if default_variation:
            default_price = default_variation.price
        else:
            default_price = product.price
    
        product.default_price =default_price
        product.best_percentage = get_best_offer(product)
        if product.best_percentage is not None:
            product.discounted_price = calculate_discounted_price(product.default_price, product.best_percentage)
        else:
            product.discounted_price = product.price

    paginator = Paginator(products, 6 if category_slug else 6)  # Use different pagination for category or all products
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
        'active_categories': active_categories
    }

    return render(request, 'store/store.html', context)




def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(
            category__slug=category_slug,
            slug=product_slug,
            is_available=True,
            category__is_active=True
        )
        product_images = ProductImage.objects.filter(product=single_product)[:3]
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

    except Product.DoesNotExist:
        return render(request, 'store/404.html')

    # Get the best offer percentage
    best_percentage = get_best_offer(single_product)

    # Calculate the discounted price if there is an offer
    default_variation = Variation.objects.filter(product=single_product.id,defult=True).first()
    if default_variation:
        price = default_variation.price
        stock=default_variation.quantity
    else:
        price = None
    #print(type(price))
    if best_percentage is not None:
        original_price = single_product.price
        discounted_price = calculate_discounted_price(price, best_percentage)
    else:
        discounted_price = None

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    variations=Variation.objects.filter(product=single_product.id)
    default_variation = Variation.objects.filter(product=single_product, defult=True).first()
    #print(variations)
    #print(discounted_price)
    #print(price,stock)
    context = {
        'single_product': single_product,
        'product_images': product_images,
        'in_cart': in_cart,
        'discounted_price': discounted_price,
        'percentage': best_percentage,
        'reviews': reviews,
        'variations':variations,
        'price':price,
        'stock':stock,
        'default_variation':default_variation
        
    }

    return render(request, 'store/product_detail.html', context)


def search(request):
    products = Product.objects.all()
    product_count = products.count()  # Initial count before filtering

    # Initialize filters
    keyword = request.GET.get('keyword', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort_by', '')

    # Apply keyword filter
    if keyword:
        products = products.filter(
            Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
        )
    
    # Apply price range filter
    if min_price and max_price:
        try:
            min_price = Decimal(min_price)
            max_price = Decimal(max_price)
            products = products.filter(price__gte=min_price, price__lte=max_price)
        except (InvalidOperation, ValueError):
            products = Product.objects.none()  # No products if price filter fails

    # Apply sorting
    if sort_by == "low_to_high":
        products = products.order_by('price')
    elif sort_by == "high_to_low":
        products = products.order_by('-price')

    # Update product count after filtering
    product_count = products.count()

    # Get best offer and discounted price for each product
    for product in products:

        default_variation = Variation.objects.filter(product=product, defult=True).first()
        if default_variation:
            default_price = default_variation.price
        else:
            default_price = product.price
    
        product.default_price = default_price
        best_offer = get_best_offer(product)

        best_percentage = get_best_offer(product)
        if best_percentage is not None:
            product.discounted_price = calculate_discounted_price(product.default_price,best_percentage)
            product.best_percentage = best_percentage
        else:
            product.discounted_price = default_price
            product.best_percentage = None

    # Render the results
    context = {
        'products': products,
        'product_count': product_count,
        'active_categories': Category.objects.filter(is_active=True),  # Assuming you need active categories
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER') 
    if request.method == 'POST':
        try:
            
            review = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thank you! Your review has been updated.')
            else:
                messages.error(request, 'Please correct the error below.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                # Create a new review
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been created.')
            else:
                messages.error(request, 'Please correct the error below.')
            return redirect(url)

    # If the request is not POST, redirect to the referring page
    return redirect(url)

@csrf_exempt
def update_selected_color(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        color = data.get('color')
        product_id = data.get('product_id')
        
        try:
            product = Product.objects.get(id=product_id)
            product_variation = Variation.objects.get(product=product, variation_value=color)
            choose_price = product_variation.price
            choose_stock = product_variation.quantity

            # Calculate the discounted price if applicable
            best_percentage = get_best_offer(product)
            if best_percentage is not None:
                discounted_price = calculate_discounted_price(choose_price, best_percentage)
            else:
                discounted_price = None
            
            return JsonResponse({
                'success': True,
                'choose_price': str(choose_price),  # Convert Decimal to string to avoid serialization issues
                'choose_stock': choose_stock,
                'discounted_price': str(discounted_price) if discounted_price else None,
                #'product_variation':product_variation
            })
        except Variation.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product variation not found'})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
