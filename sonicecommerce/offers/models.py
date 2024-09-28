from django.db import models
from category.models import Category
from store.models import Product

class Offer(models.Model):
    OFFER_TYPE_CHOICES = [
        ('category', 'Category'),
        ('product', 'Product'),
        ('referral', 'Referral'),
    ]
    
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    percentage = models.IntegerField()  # Changed field to IntegerField
    valid_from = models.DateField()
    valid_to = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.offer_type} Offer - {self.percentage}% off"
