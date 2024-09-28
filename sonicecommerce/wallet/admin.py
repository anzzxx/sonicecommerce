from django.contrib import admin
from .models import Wallet, WalletTransaction

# Register the Wallet model
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'created_at', 'updated_at')
    # Add other configurations for WalletAdmin if needed

# Register the WalletTransaction model
@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    # Add other configurations for WalletTransactionAdmin if needed
