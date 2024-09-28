
from datetime import date
from offers.models import Offer

import decimal


def calculate_discounted_price(original_price, percentage):
    # Ensure original_price is a Decimal
    if not isinstance(original_price, decimal.Decimal):
        original_price = decimal.Decimal(original_price)
    
    # Convert percentage to Decimal
    percentage = decimal.Decimal(percentage)
    
    # Perform the calculation
    discounted_price = original_price * (1 - (percentage / 100))
    
    return discounted_price


def get_best_offer(product):
    # Fetch the active product-specific offer
    product_offer = Offer.objects.filter(
        product=product,
        offer_type='product',
        is_active=True,
        valid_from__lte=date.today(),
        valid_to__gte=date.today()
    ).first()

    # Fetch the active category-specific offer
    category_offer = Offer.objects.filter(
        category=product.category,
        offer_type='category',
        is_active=True,
        valid_from__lte=date.today(),
        valid_to__gte=date.today()
    ).first()

    # Initialize variables for the best offer
    best_offer = None
    best_percentage = None

    # Determine the best offer
    if product_offer and category_offer:
        # Compare both offers
        product_discount = product_offer.percentage
        category_discount = category_offer.percentage
        best_offer = product_offer if product_discount > category_discount else category_offer
        best_percentage = best_offer.percentage
    elif product_offer:
        best_offer = product_offer
        best_percentage = best_offer.percentage
    elif category_offer:
        best_offer = category_offer
        best_percentage = best_offer.percentage

    return best_percentage