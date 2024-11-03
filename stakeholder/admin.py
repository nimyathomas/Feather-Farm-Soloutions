from django.contrib import admin
from stakeholder.models import ChickBatch, DailyData

admin.site.register(ChickBatch)
admin.site.register(DailyData)

from user.models import Supplier

from django.contrib import admin
from user.models import Supplier

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_code', 'name', 'email', 'phone_number', 'is_active')  # Fields to display in the admin list
    search_fields = ('supplier_code', 'name', 'email', 'phone_number')  # Enable search by these fields
    list_filter = ('is_active',)  # Filter by active/inactive status
    ordering = ('name',)  # Order by name (note the comma to make it a tuple)
    actions = ['delete_selected']  # Enable bulk delete

    def delete_model(self, request, obj):
        # Custom behavior for single item delete (if needed)
        obj.is_active = False  # Mark it as inactive instead of deleting
        obj.save()

    def has_delete_permission(self, request, obj=None):
        return True  # Enable delete permission for individual objects

# Register Supplier with custom admin
admin.site.register(Supplier, SupplierAdmin)
