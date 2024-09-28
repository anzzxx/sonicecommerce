from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product
from variation.models import Variation
from .models import Cart,CartItem
# Create your views here.
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Address, UserProfile
from store.pipeline import get_best_offer,calculate_discounted_price
def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart

def variation_exists(ex_var_list, product_variation):
                for sublist in ex_var_list:
                    if all(variation in sublist for variation in product_variation):
                        return True
                return False
                
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
   

   

    # Define the maximum quantity allowed per person
    MAX_QTY_PER_PERSON = 5

    if current_user.is_authenticated:
        product_variation = []

        if request.method == 'POST':
            
            selected_color = request.POST.get('selected_color')
            #print(selected_color)
            if selected_color:
                pass
            else:
                selected_variation = Variation.objects.get(product=product, defult=True)
                selected_color = selected_variation.variation_value    
            
            for item in request.POST:
                key = item
                value = request.POST[key]
                #print(key,value)
                try:
                    variation = Variation.objects.get(
                        product=product, 
                        variation_value=selected_color
                    )
                    #print(variation)
                    product_variation.append(variation)
                    #print(product_variation)
                except Variation.DoesNotExist:
                    pass
        
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        
        if is_cart_item_exists:
            
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            #id = []
            #print(f'cart item{cart_item}')
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                #id.append(item.id)
            #print(f'existing variation{existing_variation}')    
            #print(f'list ex_var list_id{id}')
            
            is_insaide=variation_exists(ex_var_list,product_variation)
            
            if is_insaide:
                variation_quary=product_variation[0]
                variation_value=variation_quary.variation_value
                
                variation=Variation.objects.get(product=product,variation_value=variation_value)
                id=variation.id
                
                
                item = CartItem.objects.get(product=product,user=request.user,variation=id)
                #print(item)

                # Check if adding one more exceeds stock
                if item.quantity + 1 > variation.quantity:
                    # Handle out of stock case
                    messages.error(request, "Not enough stock available.")
                    return redirect('cart')

                # Check if adding one more exceeds maximum allowed per person
                if item.quantity + 1 > MAX_QTY_PER_PERSON:
                    # Handle maximum quantity per person case
                    messages.error(request, f"Maximum {MAX_QTY_PER_PERSON} items allowed per person.")
                    return redirect('cart')

                item.quantity += 1
                item.save()
            else:
                #print('else')
                # Create a new cart item
                variation_quary=product_variation[0]
                variation_value=variation_quary.variation_value 
                variation=Variation.objects.get(product=product,variation_value=variation_value)
                if variation.quantity > 0:
                    item = CartItem.objects.create(
                        product=product,
                        quantity=1,
                        user=current_user
                    )
                    if len(product_variation) > 0:
                        item.variation.clear()
                        item.variation.add(*product_variation)
                    item.save()
                else:
                    messages.error(request, "Product is out of stock.")
                    return redirect('cart')
        else:
            # Create a new cart item
            variation_quary=product_variation[0]
            #print(variation_quary)
            variation_value=variation_quary.variation_value
            #print(variation_value)   
            variation=Variation.objects.get(product=product,variation_value=variation_value)
            #print(variation_id)
            #id=variation_id.id
                
                
            #item = CartItem.objects.get(product=product,user=request.user,variation=id)
            #print(item)
            if variation.quantity > 0:
                cart_item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    user=current_user
                )
                if len(product_variation) > 0:
                    cart_item.variation.clear()
                    cart_item.variation.add(*product_variation)
                cart_item.save()
            else:
                messages.error(request, "Product is out of stock.")
                return redirect('cart')

        return redirect('cart')

    # if user not authenticated
    else:
        product_variation = []

        if request.method == 'POST':
            for item in request.POST:
                selected_color = request.POST.get('selected_color')
                
                if selected_color:
                    pass
                else:
                    selected_variation = Variation.objects.get(product=product, defult=True)
                    selected_color = selected_variation.variation_value  
                key = item
                value = request.POST[key]
                #print(selected_color)
                try:
                    variation = Variation.objects.get(
                        product=product,  
                        variation_value=selected_color
                    )
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            ex_var_list = []
            #id = []

            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                print(f'existing_variation:{existing_variation}')
                print(f'ex_var_list:{ex_var_list}')
                #id.append(item.id)
            is_insaide=variation_exists(ex_var_list,product_variation)
            if is_insaide:
                #index = ex_var_list.index(product_variation)
                #item_id = id[index]
                variation_quary=product_variation[0]
                variation_value=variation_quary.variation_value
                
                variation_id=Variation.objects.get(product=product,variation_value=variation_value)
                id=variation_id.id
                item = CartItem.objects.get(product=product, variation=id)

                # Check if adding one more exceeds stock
                if item.quantity + 1 > product.stock:
                    messages.error(request, "Not enough stock available.")
                    return redirect('cart')

                # Check if adding one more exceeds maximum allowed per person
                if item.quantity + 1 > MAX_QTY_PER_PERSON:
                    messages.error(request, f"Maximum {MAX_QTY_PER_PERSON} items allowed per person.")
                    return redirect('cart')

                item.quantity += 1
                item.save()
            else:
                # Create a new cart item
                if product.stock > 0:
                    item = CartItem.objects.create(
                        product=product,
                        quantity=1,
                        cart=cart
                    )
                    if len(product_variation) > 0:
                        item.variation.clear()
                        item.variation.add(*product_variation)
                    item.save()
                else:
                    messages.error(request, "Product is out of stock.")
                    return redirect('cart')
        else:
            # Create a new cart item
            if product.stock > 0:
                cart_item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    cart=cart
                )
                if len(product_variation) > 0:
                    cart_item.variation.clear()
                    cart_item.variation.add(*product_variation)
                cart_item.save()
            else:
                messages.error(request, "Product is out of stock.")
                return redirect('cart')

    return redirect('cart')



def remove_cart(request,product_id,cart_item_id):
   
    product=get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item=CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity >1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass       
    return redirect('cart')        

def remove_cart_item(request,product_id,cart_item_id):
    
    product=get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product,user=request.user, id=cart_item_id)
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
         #cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

    cart_item.delete()
    return redirect('cart')

@login_required(login_url='login')
def cart(request, total=0, quantity=0, cart_items=None):
    cart_items = []
    tax = 0
    grand_total = 0

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            # Get the best offer for the product
            
            best_percentage = get_best_offer(cart_item.product)
            variation_price = None
            for variation in cart_item.variation.all():
                variation_price = variation.price
                variation_value = variation.variation_value
                break  # Assuming only one variation is relevant
            
            #print(type(variation_price),type(best_percentage))    
            if best_percentage:
                cart_item.discounted_price = calculate_discounted_price(int(variation_price), best_percentage)
                cart_item.total_price = cart_item.discounted_price * cart_item.quantity
            else:
                cart_item.discounted_price = None
                cart_item.total_price = variation_price * cart_item.quantity

            total += int(cart_item.total_price)
            quantity += cart_item.quantity

        tax = (2 * total / 100)
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        #'variation_price':variation_price
    }
    
    return render(request, 'store/cart.html', context)



def checkout(request, total=0, quantity=0, cart_items=None):
    cart_items = []
    tax = 0
    grand_total = 0
    saved_addresses = None
    user_profile = None

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            user_profile = UserProfile.objects.get(user=request.user)
            saved_addresses = Address.objects.filter(user_profile=user_profile)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        #discounted_price=None
        for cart_item in cart_items:
            # Get the best offer for the product
            best_percentage = get_best_offer(cart_item.product)
            variation_price = None
            for variation in cart_item.variation.all():
                variation_price = variation.price
                variation_value = variation.variation_value
                break  # Assuming only one variation is relevant
            if best_percentage:
                
                cart_item.discounted_price = calculate_discounted_price(int(variation_price), best_percentage)
                cart_item.total_price = cart_item.discounted_price * cart_item.quantity
            else:
                cart_item.discounted_price = None
                cart_item.total_price = variation_price * cart_item.quantity

        total += cart_item.total_price
        quantity += cart_item.quantity

        tax = (2 * total / 100)
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass
    try:
        # Get the UserProfile instance for the current user
        user_profile = UserProfile.objects.get(user=request.user)
        # Filter addresses based on the UserProfile instance and is_primary flag
        address = Address.objects.filter(user_profile=user_profile, is_primary=True).first()
    except UserProfile.DoesNotExist:
        address = None

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        #'saved_addresses': saved_addresses,
        'address':address,
        
    }

    return render(request, 'store/checkout.html', context)

from django.shortcuts import redirect, get_object_or_404
from .models import Product, CartItem

def increase_cart(request, product_id):
    # Get the product
    product = get_object_or_404(Product, id=product_id)
    color = request.POST['color'].lower()
    MAX_QTY_PER_PERSON=5
    
    variation=Variation.objects.get(product=product,variation_value=color)
    variation_id=variation.id
   
    if request.user.is_authenticated:
        item = CartItem.objects.get(product=product,user=request.user,variation=variation_id)
    else:
        item = CartItem.objects.get(product=product,variation=variation_id)
                # Check if adding one more exceeds stock
    if item.quantity + 1 > variation.quantity:
        # Handle out of stock case
        messages.error(request, "Not enough stock available.")
        return redirect('cart')

                # Check if adding one more exceeds maximum allowed per person
    if item.quantity + 1 > MAX_QTY_PER_PERSON:
        # Handle maximum quantity per person case
        messages.error(request, f"Maximum {MAX_QTY_PER_PERSON} items allowed per person.")
        return redirect('cart')

    item.quantity += 1
    item.save()

    return redirect('cart')  # Redirect to the cart page after increasing the quantity
   