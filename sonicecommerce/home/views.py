from django.shortcuts import render
from category.models import Category
from store.models import Product
from store.pipeline import calculate_discounted_price,get_best_offer
from variation.models import Variation

def index(request):
    active_categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(category__in=active_categories, is_available=True)
    
    for product in products:
        # Fetch default variation for each product
        default_variation = Variation.objects.filter(product=product, defult=True).first()
        if default_variation:
            default_price = default_variation.price
        else:
            default_price = product.price
    
        product.default_price =int(default_price)
        

        # Calculate the best offer percentage
        best_percentage = get_best_offer(product)
        #print(f'ans:{ product.default_price}')
        #print(f'best %{best_percentage}')
        if best_percentage is not None:
            #print(type(product.default_price),type(best_percentage))
            product.discounted_price = calculate_discounted_price(product.default_price,best_percentage)
            product.best_percentage = best_percentage
        else:
            #print('elseS')
            product.discounted_price = default_price
            product.best_percentage = None

    context = {
        'products': products,
        'active_categories': active_categories,
    }
    return render(request, 'home.html', context)
