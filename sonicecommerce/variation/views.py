from django.shortcuts import render,redirect, get_object_or_404
from .models import Variation
from django.contrib import messages
from .forms import VariationForm
from django.core.paginator import Paginator
# Create your views here.
def variation_view(request):
    variations = Variation.objects.all()
    paginator = Paginator(variations, 10)  # Show 10 variations per page
    page_number = request.GET.get('page')
    variations = paginator.get_page(page_number)
    
    context = {
        'variations': variations
    }
    return render(request, 'cadmin/variation.html', context)


def variation_create(request):
    if request.method == 'POST':
        form = VariationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Variation added successfully.')
            return redirect('variation_view')  # Redirect to a view that lists all variations
    else:
        form = VariationForm()
    return render(request, 'cadmin/variation_form.html', {'form': form})

def variation_update(request, pk):
    variation = get_object_or_404(Variation, pk=pk)
    if request.method == 'POST':
        form = VariationForm(request.POST, instance=variation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Variation updated successfully.')
            return redirect('variation_view')
    else:
        form = VariationForm(instance=variation)
    return render(request, 'cadmin/variation_form.html', {'form': form})    
    
def variation_toggle_status(request, pk):
    variation = get_object_or_404(Variation, pk=pk)
    variation.is_active = not variation.is_active
    variation.save()
    status = "enabled" if variation.is_active else "disabled"
    messages.success(request, f'Variation {status} successfully.')
    return redirect('variation_view')