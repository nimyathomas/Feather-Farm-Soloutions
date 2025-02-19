from django.urls import path
from .views import (
    hoteldashboard, view_farm, view_profile, view_orders, 
    cart_view, update_cart, checkout_view, wallet_view, add_funds_to_wallet
)
# app_name='hoteldetails'

urlpatterns = [
    path('', hoteldashboard, name="hoteldashboard"),
    path('view_profile/<int:id>', view_profile, name="view_profile"),
    path('view_orders', view_orders, name="view_orders"),
    path('view_farm/<int:farm_id>', view_farm, name='view_farm'),
    path('cart_view', cart_view, name="cart_view"),
    path('checkout_view', checkout_view, name="checkout_view"),
    path("update-cart/", update_cart, name="update_cart"),
    path('wallet/', wallet_view, name='wallet'),
    path('wallet/add-funds/', add_funds_to_wallet, name='add_funds_to_wallet'),
    path('wallet/add-funds/', add_funds_to_wallet, name='add_funds'),
    path('wallet/get-balance/', add_funds_to_wallet, name='get_balance'),
]
