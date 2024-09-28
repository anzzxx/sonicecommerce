from django.shortcuts import render,redirect
from accounts.models import Accounts 
from category.models import Category
from category.forms import CategoryForm
from django.urls import reverse_lazy 
from store.models import Product,ProductImage
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from accounts.forms import UserEditForm
from django.contrib import messages, auth
from coupon.models import Coupon
from coupon.forms import CouponForm
from store.forms import ProductForm,ProductImageFormSet
import json
from store.pipeline import get_best_offer,calculate_discounted_price
from orders.models import Order,OrderProduct,Payment,OrderRequest
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime, timedelta 
import openpyxl
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.core.paginator import Paginator
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.contrib.auth.decorators import user_passes_test
# Create your views here.
from django.core.files.base import ContentFile
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from django.db.models.functions import Cast
from wallet.models import Wallet,WalletTransaction
from decimal import Decimal
from django.utils import timezone

def admin_login(request):
    if request.user.is_authenticated and request.user.is_admin:
        
        return redirect('admin_dashbord')

    if request.method=="POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(request, email=email, password=password)

        if user is not None and user.is_admin:
            auth.login(request, user)
            return redirect('admin_dashbord')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('admin_login')   

    return render(request,'cadmin/adminlogin.html')
@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def admin_dashbord(request):
    product_count = Product.objects.filter(is_available=True).count()
    order_count = Order.objects.filter(is_orderd=True).count()

    new_order = Order.objects.filter(status='New').count()
    cancelled_order = Order.objects.filter(status='Cancelled').count()
    delivered_order = Order.objects.filter(status='Deliverd').count()
    shipped_order = Order.objects.filter(status='Shipped').count()

    # Best-selling products based on quantity sold
    best_selling_products = (OrderProduct.objects
                             .values('product__product_name')
                             .annotate(total_quantity_sold=Sum('quantity'))
                             .order_by('-total_quantity_sold')[:10])

    best_selling_category = (OrderProduct.objects
                             .values('product__category__category_name')
                             .annotate(total_category_sales=Sum('quantity'))
                             .order_by('-total_category_sales').first())

    if best_selling_category:
        top_selling_category_name = best_selling_category['product__category__category_name']
        top_selling_category_count = best_selling_category['total_category_sales']
    else:
        top_selling_category_name = "No sales yet"
        top_selling_category_count = 0

    context = {
        'product_count': product_count,
        'order_count': order_count,
        'new_order': new_order,
        'cancelled_order': cancelled_order,
        'delivered_order': delivered_order,
        'shipped_order': shipped_order,
        'best_selling_products': best_selling_products,
        'top_selling_category_name': top_selling_category_name,
        'top_selling_category_count': top_selling_category_count
    }

    return render(request, 'cadmin/dashbord.html', context)

# View to provide sales data as JS
@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def get_sales_data(request, period='month'):
    if period == 'year':
        current_year = datetime.now().year
        labels = [str(year) for year in range(current_year - 5, current_year + 1)]  # Last 5 years
        data = []
        
        # Loop through each year and calculate the total sales for that year
        for year in range(current_year - 5, current_year + 1):
            total_sales = Order.objects.filter(
                is_orderd=True, 
                created_at__year=year
            ).aggregate(total_sales=Sum('order_total'))['total_sales'] or 0
            data.append(total_sales)
    else:
        current_year = datetime.now().year
        labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        data = []
        
        # Loop through each month of the current year and calculate the total sales for that month
        for month in range(1, 13):
            total_sales = Order.objects.filter(
                is_orderd=True, 
                created_at__year=current_year, 
                created_at__month=month
            ).aggregate(total_sales=Sum('order_total'))['total_sales'] or 0
            data.append(total_sales)
    
    response = {
        'labels': labels,
        'data': data
    }

    return JsonResponse(response)

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def user_detail(request):
    users_list = Accounts.objects.all().order_by('date_joined')
    
    # Pagination: 10 users per page
    paginator = Paginator(users_list, 10)  
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users
    }
    return render(request, 'cadmin/users.html', context)
@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def block_user(request,user_id):
    try:
        user = Accounts.objects.get(id=user_id)
        user.is_active = False
        user.save()
    except Accounts.DoesNotExist:
         messages.error(request, 'User not found.')
    return redirect('user_detail_page')

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def unblock_user(request, user_id):
    try:
        user = Accounts.objects.get(id=user_id)
        user.is_active = True
        user.save()
    except Accounts.DoesNotExist:
        messages.error(request, 'User not found.')
    return redirect('user_detail_page')

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def product_details(request):
    products = Product.objects.all()
    paginator = Paginator(products, 10)  # 1 product per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products
    }
    return render(request, 'cadmin/product_details.html', context)

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        formset = ProductImageFormSet(request.POST, request.FILES, prefix='images')

        if product_form.is_valid() and formset.is_valid():
            product = product_form.save(commit=False)
            product.save()

            # Save the images from the formset
            for form in formset.cleaned_data:
                if form:
                    image = form['image']  # Access the image field from the cleaned data
                    ProductImage.objects.create(product=product, image=image)

            return JsonResponse({'success': True, 'message': 'Product added successfully'})
        else:
            errors = {
                'product_errors': product_form.errors.as_json(),
                'formset_errors': json.dumps(formset.errors)
            }
            return JsonResponse({'success': False, 'message': 'Form validation failed', 'errors': errors})
            

    else:
        product_form = ProductForm()
        formset = ProductImageFormSet(prefix='images')
        return render(request, 'cadmin/add_product.html', {
            'product_form': product_form,
            'formset': formset,
        })
    return redirect('product_detail_page')    

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        
        if form.is_valid() and formset.is_valid():
            #if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect(reverse_lazy('product_detail_page'))  # Redirect to the admin panel or another page
        else:
            messages.error(request, 'Please correct product details or image uploads.')
            #print(form.errors) 
            #print(formset.error)
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)
    
    return render(request, 'cadmin/edit_product.html', {'form': form, 'formset': formset, 'product': product})

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def delete_product_image(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)
    image.delete()
    return redirect(request.META.get('HTTP_REFERER', 'product_detail_page'))    

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def disable_product(request,product_id):
    product=get_object_or_404(Product, id=product_id)
    product.is_available=False
    product.save()
    return redirect(reverse_lazy('product_detail_page'))

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def enable_product(request,product_id):
    product=get_object_or_404(Product, id=product_id)
    product.is_available=True
    product.save()
    return redirect(reverse_lazy('product_detail_page'))

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def category_detail(request):
    categories = Category.objects.all()
    paginator = Paginator(categories, 10)  # 10 categories per page
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number)
    context={
        'categories':categories,
    }
    return render(request,'cadmin/categorydetail.html',context)


@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category_datail_page')  # Replace with your desired redirect
    else:
        form = CategoryForm()

    return render(request, 'cadmin/add_category.html', {'form': form})

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            if form.is_valid():
                form.save()
                return redirect('category_datail_page')  # Redirect to category detail page
            else:
                print(form.errors) 
                print(formset.error)
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'cadmin/edit_category.html', {'form': form,'category': category}) 

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")    
def desable_category(request,category_id):
    category=get_object_or_404(Category, id=category_id)
    category.is_active=False
    category.save()
    return redirect(request.META.get('HTTP_REFERER', 'category_datail_page'))    

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")  
def enable_category(request,category_id):
    category=get_object_or_404(Category, id=category_id)
    category.is_active=True
    category.save()
    return redirect(request.META.get('HTTP_REFERER', 'category_datail_page'))  

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def coupon_detail(request):
    coupons = Coupon.objects.all()
    paginator = Paginator(coupons, 10)  # Show 10 coupons per page
    page_number = request.GET.get('page')
    coupons = paginator.get_page(page_number)
    
    context = {
        'coupons': coupons  # Fixed typo from 'coupens' to 'coupons'
    }
    return render(request, 'cadmin/coupon_detail.html', context)

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('coupon_detail')  # Redirect to the list view after saving
    else:
        form = CouponForm()
    return render(request, 'cadmin/add_coupon.html', {'form': form})

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def delete_coupon(request,id):
    coupon = get_object_or_404(Coupon, id=id)
    coupon.delete()
    messages.success(request, 'Coupon successfully deleted.')
    return redirect('coupon_detail') 


#inventery

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    paginator = Paginator(orders, 4)  # Show 10 orders per page
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {
        'orders': orders
    }
    return render(request, 'cadmin/order_list.html', context)

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        order.status = status
        if status == 'Cancelled':
            # Revert stock if order is cancelled
            order_products = OrderProduct.objects.filter(order=order)
            for item in order_products:
                product = item.product
                product.stock += item.quantity
                product.save()
        order.save()
        messages.success(request, 'Order status updated successfully.')
        return redirect('order_detail', order_id=order.id)
    return redirect('order_list')

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'Cancelled'
    order.save()

    order_products = OrderProduct.objects.filter(order=order)
    for item in order_products:
        product = item.product
        product.stock += item.quantity  # Return stock
        product.save()

    messages.success(request, 'Order cancelled and stock updated.')
    return redirect('order_detail', order_id=order.id)


@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def change_order_status(request, order_id, status):
    order = get_object_or_404(Order, order_number=order_id)
    
    # Update the status
    if status in dict(Order.STATUS).keys():
        order.status = status
        order.save()
        messages.success(request, f"Order status updated to {status}.")
    else:
        messages.error(request, "Invalid status.")
    
    return redirect('order_list')    

from django.db.models import Sum

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def sale_report(request):
    # Get the query parameters from the request
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    period_type = request.GET.get('periodType')
    
    # Initialize the orders query
    orders = Order.objects.filter(is_orderd=True).order_by('-created_at')

    # Apply filters based on period_type
    if period_type:
        if period_type == 'week':
            orders = orders.filter(created_at__gte=datetime.now() - timedelta(days=7))
        elif period_type == 'day':
            orders = orders.filter(created_at__gte=datetime.now() - timedelta(days=1))
        elif period_type == 'month':
            orders = orders.filter(created_at__gte=datetime.now() - timedelta(days=30))
    else:
        # Filter by date range if both start_date and end_date are provided
        if start_date and end_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                orders = orders.filter(created_at__range=[start_date_obj, end_date_obj])
            except ValueError:
                orders = orders.none()
        elif not start_date and not end_date and not period_type:
            start_date = end_date = datetime.now().strftime('%Y-%m-%d')
            orders = orders.filter(created_at__date=datetime.now().date())

    # Paginate the orders
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate total discount for each order
    order_discounts = []
    for order in page_obj:
        order_products = OrderProduct.objects.filter(order=order)
        total_discount = 0
        for order_product in order_products:
            product = order_product.product
            best_percentage = get_best_offer(product)
            variation_price = None

            for variation in order_product.variation.all():
                variation_price = variation.price
                break  # Assuming you want only the first variation
            
            if best_percentage and variation_price:
                disc_amount = calculate_discounted_price(variation_price, best_percentage)
                total_discount += (variation_price - disc_amount)
        
        order_discounts.append({
            'order': order,
            'total_discount': total_discount
        })

    # Calculate overall metrics
    overall_sales_count = orders.count()
    overall_amount = orders.aggregate(total_amount=Sum('order_total'))['total_amount'] or 0
    overall_coupon = orders.aggregate(
    total_coupon=Sum(Cast('coupon', FloatField())))['total_coupon'] or 0
    # Calculate total discount
    overall_discount = 0
    for order in orders:
        order_products = OrderProduct.objects.filter(order=order)
        for order_product in order_products:
            product = order_product.product
            best_percentage = get_best_offer(product)
            variation_price = None

            for variation in order_product.variation.all():
                variation_price = variation.price
                break  # Assuming you want only the first variation
            
            if best_percentage and variation_price:
                disc_amount = calculate_discounted_price(variation_price, best_percentage)
                overall_discount += (variation_price - disc_amount)
    
    context = {
        'orders': page_obj,
        'start_date': start_date,
        'end_date': end_date,
        'period_type': period_type,
        'order_discounts': order_discounts,
        'overall_sales_count': overall_sales_count,
        'overall_amount': overall_amount,
        'overall_discount': overall_discount,
        'overall_coupon':overall_coupon
    }
    return render(request, 'cadmin/sale_report.html', context)



@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def download_excel(request):
    # Get the query parameters from the request
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    period_type = request.GET.get('periodType')
    
    # Initialize the orders query
    orders = Order.objects.filter(is_orderd=True).order_by('-created_at')

    # Apply filters based on period_type
    if period_type:
        if period_type == 'week':
            orders = orders.filter(created_at__gte=datetime.now() - timedelta(days=7))
        elif period_type == 'day':
            orders = orders.filter(created_at__gte=datetime.now() - timedelta(days=1))
        elif period_type == 'month':
            orders = orders.filter(created_at__gte=datetime.now() - timedelta(days=30))
    else:
        # Filter by date range if both start_date and end_date are provided
        if start_date and end_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                orders = orders.filter(created_at__range=[start_date_obj, end_date_obj])
            except ValueError:
                orders = orders.none()
        elif not start_date and not end_date and not period_type:
            start_date = end_date = datetime.now().strftime('%Y-%m-%d')
            orders = orders.filter(created_at__date=datetime.now().date())
    # Create an in-memory workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Sales Report'

    # Define headers
    headers = ['Order Number', 'Customer', 'Order Total', 'Quantity', 'Status', 'Coupon','Total Disc']
    worksheet.append(headers)

    # Write data rows
    for order in orders:
        quantity = ', '.join([str(p.quantity) for p in order.orderproduct_set.all()])
        worksheet.append([
            order.order_number,
            order.first_name,  # Ensure you're accessing attributes, not methods
            order.order_total,
            quantity,
            order.status,
            order.coupon if order.coupon else 'N/A',  # Access the coupon's code attribute
            
        ])

    # Create an HTTP response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'
    workbook.save(response)
    return response

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def download_pdf(request):
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    period_type = request.GET.get('periodType')
    
    # Initialize the orders query
    orders = Order.objects.filter(is_orderd=True).order_by('-created_at')

    # Apply filters based on period_type
    if period_type:
        if period_type == 'week':
            orders = orders.filter(created_at__gte=datetime.now() - timedelta(days=7))
        elif period_type == 'day':
            orders = orders.filter(created_at__gte=datetime.now() - timedelta(days=1))
        elif period_type == 'month':
            orders = orders.filter(created_at__gte=datetime.now() - timedelta(days=30))
    else:
        # Filter by date range if both start_date and end_date are provided
        if start_date and end_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                orders = orders.filter(created_at__range=[start_date_obj, end_date_obj])
            except ValueError:
                orders = orders.none()
        elif not start_date and not end_date and not period_type:
            start_date = end_date = datetime.now().strftime('%Y-%m-%d')
            orders = orders.filter(created_at__date=datetime.now().date())
    # Create a PDF in memory
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Define header
    p.setFont("Helvetica-Bold", 12)
    p.drawString(30, height - 50, "Sales Report")

    # Define table headers
    p.setFont("Helvetica-Bold", 10)
    headers = ['Order Number', 'Customer', 'Order Total', 'Quantity', 'Status', 'Coupon']
    x_offset = 30
    y_offset = height - 80
    for header in headers:
        p.drawString(x_offset, y_offset, header)
        x_offset += 100

    # Write data rows
    p.setFont("Helvetica", 10)
    for order in orders:
        y_offset -= 20
        x_offset = 30
        p.drawString(x_offset, y_offset, str(order.order_number))
        x_offset += 100
        p.drawString(x_offset, y_offset, order.first_name)
        x_offset += 100
        p.drawString(x_offset, y_offset, f"${order.order_total:.2f}")
        x_offset += 100
        quantity = ', '.join([str(p.quantity) for p in order.orderproduct_set.all()])
        p.drawString(x_offset, y_offset, quantity)
        x_offset += 100
        p.drawString(x_offset, y_offset, order.status)
        #x_offset += 100
        #p.drawString(x_offset, y_offset, order.coupon.code if order.coupon else 'N/A')

    # Finalize and save PDF
    p.showPage()
    p.save()
    buffer.seek(0)

    # Create an HTTP response with the PDF file
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=sales_report.pdf'
    return response

#@user_passes_test(lambda u:u.is_superadmin,login_url="admin_login")
@login_required
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out')
    return redirect('admin_login')

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def manage_order_requests(request):
    order_requests = OrderRequest.objects.filter(status='pending')  # Get all pending requests
    return render(request, 'cadmin/admin_order_requests.html', {'order_requests': order_requests})

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def approve_or_reject_request(request, request_id, action,user):
    order_request = get_object_or_404(OrderRequest, id=request_id)
    user=Accounts.objects.get(id=user)
    if action == 'approve':
        order_request.status = 'approved'
        # Implement the logic for canceling or returning the order (e.g., updating order status)
        order_request.order.status = 'cancelled' if order_request.request_type == 'cancel' else 'returned'
        order= order_request.order
        wallet = get_object_or_404(Wallet, user=user)
        amount_paid = Decimal(order.payment.amount_paid)
        if order.payment.status == 'COMPLETED':
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount_paid,
                transaction_type="Credited"
            )
            wallet.balance +=amount_paid
            wallet.save()
            print('wallet save')
        else:
            pass    

        order_request.order.save()

    elif action == 'reject':
        order_request.status = 'rejected'

    order_request.save()
    return redirect('manage_order_requests')    

@user_passes_test(lambda u: u.is_authenticated and u.is_superadmin, login_url="admin_login")
def cadmin_order_details(request,order_id):
    order=Order.objects.get(order_number=order_id)
    order_detail = OrderProduct.objects.filter(order=order)
    request_exist = OrderRequest.objects.filter(order=order).exists() 
    request_status = OrderRequest.objects.filter(order=order).first() 
    sub_total=0
    for i in order_detail:
        sub_total +=i.product_price*i.quantity
    context={
        'order_detail':order_detail,
        'order':order,
        'sub_total':sub_total,
        'request_exist':request_exist,
        'request_status':request_status

    }
    return render(request,'cadmin/order_detail.html',context)    