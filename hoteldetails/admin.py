from django.contrib import admin
from .models import Order, Cart, CartItem, HotelUser

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(HotelUser)
