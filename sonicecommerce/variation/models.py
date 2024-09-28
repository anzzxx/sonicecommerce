from django.db import models
from store.models import Product

# Choices for variation category
VARIATION_CATEGORY_CHOICES = (
    ('color', 'Color'),
    ('size', 'Size'),
)

class VariationManager(models.Manager):
    def colors(self):
        """Return all variations that are of category 'color' and are active."""
        return self.filter(variation_category='color', is_active=True)

    def sizes(self):
        """Return all variations that are of category 'size' and are active."""
        return self.filter(variation_category='size', is_active=True)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=VARIATION_CATEGORY_CHOICES, db_index=True)
    variation_value = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    defult=models.BooleanField(default=False,db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_date = models.DateField(auto_now=True)

    objects = VariationManager()

    def clean(self):
        """Ensure that price and quantity are not negative."""
        if self.price < 0:
            raise ValidationError('Price cannot be negative.')
        if self.quantity < 0:
            raise ValidationError('Quantity cannot be negative.')

    def __str__(self):
        """Return a string representation of the variation."""
        return f"{self.variation_category.capitalize()}: {self.variation_value} - ${self.price:.2f} ({self.quantity} in stock)"

    class Meta:
        """Meta options for the Variation model."""
        verbose_name = "Variation"
        verbose_name_plural = "Variations"

