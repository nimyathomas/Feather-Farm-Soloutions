from django.contrib import admin
from .models import Order,Cart,CartItem

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)

