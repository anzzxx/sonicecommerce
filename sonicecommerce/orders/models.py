from django.db import models
from accounts.models import Accounts
from variation.models import Variation
from store.models import Product
# Create your models here.
class Payment(models.Model):
    user=models.ForeignKey(Accounts,on_delete=models.CASCADE)
    payment_id=models.CharField(max_length=100,blank=True)
    payment_method=models.CharField(max_length=100)
    amount_paid=models.CharField(max_length=100)
    status=models.CharField(max_length=100,default='pending')
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS=(
        ('New','New'),
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
        ('Shipped','Shipped'),
        ('Deliverd','Deliverd'),
        ('Returned','Returned')
    )   

    user=models.ForeignKey(Accounts,on_delete=models.SET_NULL,null=True)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    order_number=models.CharField(max_length=20)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone=models.CharField(max_length=15)
    email=models.EmailField(max_length=50)
    address_line_1=models.CharField(max_length=50)
    address_line_2=models.CharField(max_length=50,blank=True)
    country=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    postal_code=models.CharField(max_length=10,blank=True)
    order_total=models.FloatField()
    tax=models.FloatField()
    status=models.CharField(max_length=10,choices=STATUS,default='New')
    ip=models.CharField(max_length=20,blank=True)
    is_orderd=models.BooleanField(default=False)
    coupon = models.CharField(max_length=20, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    #payment_method = models.CharField(max_length=20, default='COD')  # Add this line


    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
    def __str__(self):
        return self.first_name
    
class OrderProduct(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    user=models.ForeignKey(Accounts,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation=models.ManyToManyField( Variation,blank=True)
    quantity=models.IntegerField()
    product_price=models.FloatField()
    orderd=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.product.product_name
    

class OrderRequest(models.Model):
    REQUEST_CHOICES = [
        ('cancel', 'Cancel'),
        ('return', 'Return'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='requests')
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=10, choices=REQUEST_CHOICES)
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_request_type_display()} ({self.get_status_display()})"    