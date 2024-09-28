from django.shortcuts import render
from .models import Wallet,WalletTransaction
from django.core.paginator import Paginator

def wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')

    # Pagination
    paginator = Paginator(transactions, 5)  # Show 5 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'wallet': wallet,
        'page_obj': page_obj,
    }
    return render(request, 'account/wallet.html', context)