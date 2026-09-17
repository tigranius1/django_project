from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name', 'phone', 'is_admin', 'is_moderator', 'is_staff')
    list_filter = ('is_admin', 'is_moderator', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'full_name', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Доп. информация', {'fields': ('full_name', 'phone', 'is_admin', 'is_moderator')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Доп. информация', {'fields': ('full_name', 'phone', 'is_admin', 'is_moderator')}),
    )