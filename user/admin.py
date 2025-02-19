from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserType, Vaccine

# this fields is for add these data to adminpanel


class UserAdmin(DefaultUserAdmin):
    model = User
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "full_name",
                    "phone_number",
                    "user_type",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "full_name",
                    "password1",
                    "password2",
                    "user_type",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    list_display = (
        "email",
        "full_name",
        "phone_number",
        "user_type",
        "is_staff",
        "is_active",
    )
    list_filter = ("user_type", "is_staff", "is_active")
    search_fields = ("email", "full_name", "phone_number")
    ordering = ("email",)


admin.site.register(User, UserAdmin)
admin.site.register(UserType)

@admin.register(Vaccine)
class VaccineAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'batch_number', 'vaccination_day', 'current_stock', 'minimum_stock_level', 'stock_status')
    list_filter = ('vaccination_day', 'stock_status')
    search_fields = ('name', 'manufacturer')
