from django.urls import path
from . import views

urlpatterns = [
    path('',views.admin_login,name='admin_login'),
    path('dasbord/',views.admin_dashbord,name='admin_dashbord'),
    path('userview/',views.user_detail,name='user_detail_page'),
    path('product_detail/',views.product_details,name='product_detail_page'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),
   
    path('edit-product/<int:product_id>/',views.edit_product, name='edit_product'),
    path('delete-product-image/<int:image_id>/',views.delete_product_image, name='delete_product_image'),
    path('add-product/',views.add_product, name='add_product'),
    path('category-detail/',views.category_detail,name='category_datail_page'),
    path('desable-product/<int:product_id>/',views.disable_product,name="disable_product"),
    path('enable-product/<int:product_id>/',views.enable_product,name="enable_product"),
    path('add-category/',views.add_category,name="add_category"),
    path('edit-category/<int:category_id>/',views.edit_category,name="edit_category"),
    path('desable-category/<int:category_id>/',views.desable_category,name="desable_category"),
    path('enable-category/<int:category_id>/',views.enable_category,name="enable_category"),
    path('coupon-detail/',views.coupon_detail,name="coupon_detail"),
    
    path('add_coupon/', views.add_coupon, name='add_coupon'),
    path('admin/order-requests/', views.manage_order_requests, name='manage_order_requests'),
    path('delete_coupon/<int:id>/', views.delete_coupon, name='delete_coupon'),
    

    # Order Management URLs
    path('order-list/', views.order_list, name='order_list'),
    #path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('admin/order-request/<int:request_id>/<str:action>/<int:user>/',views.approve_or_reject_request, name='approve_or_reject_request'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),


    path('change-status/<int:order_id>/<str:status>/',views.change_order_status, name='change_order_status'),
    path('sale_report/',views.sale_report, name='sale_report'),
    path('download_excel/',views.download_excel, name='download_excel'),
    path('download_pdf/',views.download_pdf, name='download_pdf'),

    path('logoutt/',views.logout,name="logoutt"),

    path('get_sales_data/<str:period>/', views.get_sales_data, name='get_sales_data'),
    path('cadmin_order_details/<int:order_id>/',views.cadmin_order_details,name='cadmin_order_details'),
]
