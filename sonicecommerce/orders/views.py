from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse, HttpResponseRedirect
from carts.models import CartItem,Cart
from .forms import OrderForm,OrderRequestForm
from django.urls import reverse
from store.pipeline import get_best_offer,calculate_discounted_price
import datetime
from urllib.parse import urlencode
from accounts.models import Address
from store.models import Product
from .models import Order,Payment,OrderProduct,OrderRequest
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.template.loader import get_template
from coupon.models import Coupon
from decimal import Decimal
import json
from wallet.models import Wallet,WalletTransaction
from store.pipeline import get_best_offer,calculate_discounted_price
from decimal import Decimal
from django.shortcuts import HttpResponseRedirect, reverse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import timezone

# Get current date and time

# Create your views here.


@login_required
def cod_payment(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        try:
            order = Order.objects.get(order_number=order_id, user=request.user)
        except Order.DoesNotExist:
            return HttpResponse('Order not found')

        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            payment_id=f"COD-{order_id}",
            payment_method='Cash on Delivery',
            amount_paid=str(order.order_total),  # Assuming order has a field order_total
            status='pending'
        )

        # Update the order with the payment
        order.payment = payment
        order.is_orderd = True
        order.save()

        # Move cart items to OrderProduct and reduce the stock
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            best_percentage = get_best_offer(item.product)
            variation_price = None
            variation_value = None
    
            # Loop through the variations to get the price and value
            for variation in item.variation.all():
                variation_price = variation.price
                variation_value = variation.variation_value
        
                # Reduce the stock for the variation
                variation.quantity -= item.quantity
                variation.save()
                break  # Assuming only one variation is relevant (remove break if multiple are needed)

            if best_percentage:
                order.price = calculate_discounted_price(int(variation_price), best_percentage)
            else:
                order.price = variation_price

            order_product = OrderProduct()
            order_product.order_id = order.id
            order_product.payment = payment
            order_product.user_id = request.user.id
            order_product.product_id = item.product_id
            order_product.quantity = item.quantity
            order_product.product_price =  order.price
            order_product.orderd = True
            order_product.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variation.all()
            order_product.variation.set(product_variation)
            order_product.save()

            # Reduce the stock quantity
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        # Clear the cart
        CartItem.objects.filter(user=request.user).delete()

        # Send order received email
        mail_subject = 'Thank you for your order'
        message = render_to_string('orders/order_recieved_email.html', {
            'user': request.user,
            'order': order
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        # Redirect to order_complete with query parameters
        return HttpResponseRedirect(f"{reverse('order_complete')}?order_number={order.order_number}&payment_id={payment.payment_id}")

    else:
        return redirect('place_order')
@login_required
def payments(request):
    body=json.loads(request.body)
    order=Order.objects.get(user=request.user,is_orderd=False,order_number=body['orderID'])
    #store trans details
    if body['status'] =='faild':
        return redirect('payment_failed')
    payment=Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],


    )
    payment.save()
    order.payment=payment
    order.is_orderd=True
    order.save()
    #move cartitems orderproduct table
    cart_items=CartItem.objects.filter(user=request.user)

    for item in cart_items:

        best_percentage = get_best_offer(item.product)
        variation_price = None
        variation_value = None
    
        # Loop through the variations to get the price and value
        for variation in item.variation.all():
            variation_price = variation.price
            variation_value = variation.variation_value
        
            # Reduce the stock for the variation
            variation.quantity -= item.quantity
            variation.save()
            break  # Assuming only one variation is relevant (remove break if multiple are needed)

        if best_percentage:
            order.price = calculate_discounted_price(int(variation_price), best_percentage)
        else:
            order.price = variation_price 
            
        orderproduct=OrderProduct()
        orderproduct.order_id=order.id
        orderproduct.payment=payment
        orderproduct.user_id=request.user.id
        orderproduct.product_id=item.product_id
        orderproduct.quantity=item.quantity
        orderproduct.product_price= order.price
        orderproduct.orderd=True
        orderproduct.save()

        cart_item=CartItem.objects.get(id=item.id)
        product_variation=cart_item.variation.all()
        orderproduct=OrderProduct.objects.get(id=orderproduct.id)

        orderproduct.variation.set(product_variation)
        orderproduct.save()

        #reduse the qty
        product=Product.objects.get(id=item.product_id)
        product.stock -=item.quantity
        product.save()

   
     #clear the cart
    CartItem.objects.filter(user=request.user).delete()

    #send order recived mail 
    mail_subject='Thank you for your order'
    message=render_to_string('orders/order_recieved_email.html',{
        'user'  :request.user,
        'order':order
        
    })
    to_email=request.user.email
    send_email=EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()

    #send order no or transaction id 
    data={
        'order_number':order.order_number,
        'transID':payment.payment_id,
        
    }

    return JsonResponse(data)

@login_required
def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('storepage')

    grand_total = 0
    tax = 0
    total = total
    delivery_charge=2
   
    for cart_item in cart_items:
            # Get the best offer for the product
        best_percentage = get_best_offer(cart_item.product)
        variation_price = None
        for variation in cart_item.variation.all():
            variation_price = variation.price
            variation_value = variation.variation_value
            break 

        if best_percentage:
                
            cart_item.discounted_price = calculate_discounted_price(int(variation_price), best_percentage)
            cart_item.total_price = cart_item.discounted_price * cart_item.quantity
        else:
            cart_item.discounted_price = None
            cart_item.total_price = variation_price * cart_item.quantity

        total += int(cart_item.total_price)
        quantity += cart_item.quantity
    
    # Check if a coupon is applied
    coupon_discount = 0
    if 'coupon_id' in request.session:
        try:
            coupon = Coupon.objects.get(id=request.session['coupon_id'])
            coupon_discount = coupon.discount_amount
            del request.session['coupon_id']
            del request.session['discount_amount']
        except Coupon.DoesNotExist:
            coupon_discount = 0 

    # Apply coupon discount
    tax = (2 * total / 100)
    grand_total = delivery_charge+ total + tax - int(coupon_discount)
    coupon_discount=int(coupon_discount)
    try:
        address = Address.objects.get(user_profile=request.user.userprofile, is_primary=True)
    except Address.DoesNotExist:
        return redirect('storepage')  # Or handle it appropriately

    # Create the Order
    data = Order()
    data.user = current_user
    data.first_name = current_user.first_name
    data.last_name = current_user.last_name
    data.phone = address.phone_primary
    data.email = current_user.email
    data.address_line_1 = address.address_line_1
    data.address_line_2 = address.address_line_2
    data.country = address.country
    data.state = address.state
    data.city = address.city
    data.postal_code = address.postal_code
    data.order_total = grand_total
    data.tax = tax
    data.coupon = coupon_discount
    data.ip = request.META.get('REMOTE_ADDR')
    data.save()

    # Generate order id
    yr = int(datetime.date.today().strftime('%Y'))
    dt = int(datetime.date.today().strftime('%d'))
    mt = int(datetime.date.today().strftime('%m'))
    d = datetime.date(yr, mt, dt)
    current_date = d.strftime("%y%m%d")
    order_number = current_date + str(data.id)
    data.order_number = order_number
    data.save()

    # Get the order
    order = Order.objects.get(user=current_user, is_orderd=False, order_number=order_number)
    wallet=Wallet.objects.get(user=request.user)
    now = timezone.now()
    valid_coupons = Coupon.objects.filter(
    is_active=True,
    valid_from__lte=now,  # Valid from date is before or equal to current date
    valid_to__gte=now     # Valid to date is after or equal to current date
    )
    context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'wallet':wallet,
        'coupon_discount':coupon_discount,
        'valid_coupons':valid_coupons
        
    }

    return render(request, 'orders/payments.html', context)

     

@login_required
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_orderd=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
         
        subtotal = 0
        for item in ordered_products:
            subtotal += item.product_price * item.quantity

        # Get the payment details, filtering by both payment_id and order to ensure a unique match
        payment = Payment.objects.filter(payment_id=transID, order=order).first()

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id if payment else None,
            'subtotal': subtotal,
            'payment_method': payment.payment_method if payment else None,
        }

        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('homepage')

@login_required
def wallet_payment(request, id):
    order_id = id
    try:
        order = Order.objects.get(order_number=order_id, user=request.user)
    except Order.DoesNotExist:
        return HttpResponse('Order not found')

    wallet = Wallet.objects.get(user=request.user)
    wallet.balance = Decimal(wallet.balance)
    order_total = Decimal(order.order_total)

    # Check if wallet balance is enough for payment
    if order_total > wallet.balance:
        return HttpResponse('Insufficient wallet balance')

    # Create payment record
    payment = Payment.objects.create(
        user=request.user,
        payment_id=f"WP-{order_id}",
        payment_method='Wallet',
        amount_paid=str(order_total),
        status='COMPLETED'
    )

    # Update the order with the payment
    order.payment = payment
    order.is_orderd = True
    order.save()

    # Deduct the order total from the wallet balance
    wallet.balance -= order_total
    wallet.save()

    # Create a wallet transaction record
    WalletTransaction.objects.create(
        wallet=wallet,
        amount=order_total,
        transaction_type="Debit"
    )

    # Move cart items to OrderProduct and reduce the stock
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        best_percentage = get_best_offer(item.product)
        variation = item.variation.first()  # Assuming only one variation
        if variation:
            variation_price = variation.price
            variation_value = variation.variation_value

            # Reduce stock for the variation
            variation.quantity -= item.quantity
            variation.save()

        # Calculate the price with discount (if applicable)
        if best_percentage:
            product_price = calculate_discounted_price(int(variation_price), best_percentage)
        else:
            product_price = variation_price

        # Create order product record
        order_product = OrderProduct.objects.create(
            order=order,
            payment=payment,
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            product_price=product_price,
            orderd=True
        )

        # Set product variations for the order product
        product_variation = item.variation.all()
        order_product.variation.set(product_variation)

        # Reduce product stock
        product = item.product
        product.stock -= item.quantity
        product.save()

    # Clear the cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order received email
    mail_subject = 'Thank you for your order'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()  # Uncomment this line to enable email sending

    # Redirect to order_complete with query parameters
    return HttpResponseRedirect(f"{reverse('order_complete')}?order_number={order.order_number}&payment_id={payment.payment_id}")


    
    
   
@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(Order, id=order_id)
    wallet = get_object_or_404(Wallet, user=request.user)
    amount_paid = Decimal(order.payment.amount_paid)

    
    if order.payment.status == 'COMPLETED':
        
        # Create a new wallet transaction for the deposit
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount_paid,
            transaction_type="Credited"
        )
        wallet.balance +=amount_paid
        wallet.save()
        order.status = 'Cancelled'
        order.save()
        return redirect('my_orders')
    else:
        order.status = 'Cancelled'
        order.save()
        return redirect('my_orders')

@login_required
def return_order(request,order_id):

    order = Order.objects.get(id=order_id)
    wallet = get_object_or_404(Wallet, user=request.user)
    amount_paid = Decimal(order.payment.amount_paid)
    url = request.META.get('HTTP_REFERER')
    if order.payment.status == 'COMPLETED':
        # Create a new wallet transaction for the deposit
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount_paid,
            transaction_type="Credited"
        )
        wallet.balance +=amount_paid
        wallet.save()
        order.status = 'Returned'
        order.save()
        return redirect('my_orders')
    else:
        order.status = 'Returned'
        order.save()
        return redirect('my_orders')

    # Assign the 'Cancelled' status to the order
    order.status = 'Returned'
    order.save()

    return redirect(url)    
@login_required
def invoice(request,order_id):
    order_detail=OrderProduct.objects.filter(order__order_number=order_id)
    order=Order.objects.get(order_number=order_id)
    sub_total=0
    for i in order_detail:
        sub_total +=i.product_price*i.quantity
    context={
        'order_detail':order_detail,
        'order':order,
        'sub_total':sub_total

    }
    return render(request,'account/invoice.html',context)    


def download_invoice(request, order_id):
    # Fetch the order and details
    order = get_object_or_404(Order, order_number=order_id)
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    
    # Calculate subtotal
    sub_total = sum(i.product_price * i.quantity for i in order_detail)
   
    context = {
        'order': order,
        'order_detail': order_detail, 
        'sub_total': sub_total,
    }

    # Render only the specific part of the template to HTML
    template_path = 'account/invoice_div.html'  # Use a dedicated template
    template = get_template(template_path)
    html = template.render(context)

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_number}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response
@login_required
def payment_success(request):
    return HttpResponse('payment sucess')  

def request_cancel_or_return(request, order_id):
    order_num=Order.objects.get(id=order_id)
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderRequestForm(request.POST)
        if form.is_valid():
            order_request = form.save(commit=False)
            order_request.user = request.user
            order_request.order = order
            order_request.save()
            # Notify admin or redirect to a success page
            return redirect('order_details', order_id=order_num.order_number)  # Adjust to your template or view
    else:
        form = OrderRequestForm()

    return render(request, 'orders/request_cancel_or_return.html', {'form': form, 'order': order})    

def payment_failed(request):
    
    return render(request,'orders/payment_failed.html')    