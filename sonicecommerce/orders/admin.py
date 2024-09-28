from django.contrib import admin
from .models import Payment,Order,OrderProduct
# Register your models here.

class OrderProductInline(admin.TabularInline):
    model=OrderProduct
    readonly_fields=('payment','user','product','quantity','product_price','orderd')
    extra=0
class OrderAdmin(admin.ModelAdmin):
    list_display=['order_number','full_name','email','city','order_total','tax','status','is_orderd','created_at']
    list_filter=['status','is_orderd']
    search_fields=['order_number','first_name','last_name','email','phone']
    list_per_page=20
    inlines=[OrderProductInline]
from .models import OrderRequest


class OrderRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'request_type', 'status', 'created_at', 'updated_at')
    list_filter = ('request_type', 'status', 'created_at')
    search_fields = ('user__username', 'order__id', 'reason')
    ordering = ('-created_at',)

admin.site.register(Order,OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)
admin.site.register(OrderRequest)