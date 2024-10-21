from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserType

# this fields is for add these data to adminpanel


class UserAdmin(DefaultUserAdmin):
    model = User
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
         'fields': ('full_name', 'phone_number', 'user_type')}),
        (_('Coop Information'), {
         'fields': ('length', 'breadth', 'coopcapacity', 'expiry_date', 'pollution_certificate', 'farm_image','plan_file')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'user_type', 'is_staff', 'is_active'),
        }),
    )
    list_display = ('email', 'full_name', 'phone_number',
                    'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('email', 'full_name', 'phone_number')
    ordering = ('email',)


admin.site.register(User, UserAdmin)
admin.site.register(UserType)
