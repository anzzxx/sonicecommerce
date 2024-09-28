from django.db import models
from accounts.models import Accounts
from store.models import Product
from django.urls import reverse
from variation.models import  Variation  
from django.contrib.auth import get_user_model

User = get_user_model()  # Use the custom user model if you have one

class Wishlist(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)  # Add variations field
    added_date = models.DateTimeField(auto_now_add=True)

    def get_url(self):
        return reverse('product_detail', args=[self.product.category.slug, self.product.slug])

    def __str__(self):
        return f'{self.user.username} - {self.product.product_name}'
