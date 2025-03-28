from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Add the 'nickname' field to the list display, form, and fieldsets
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'nickname') # Add nickname here

    # Add nickname to the fieldsets displayed on the change user page
    # Copy the default fieldsets and add nickname to the appropriate section
    # (usually the first one with username, first_name, last_name, email)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'nickname')}), # Add nickname here
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Add nickname to the fieldsets displayed on the add user page
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('nickname',)}),
    )


# Register your CustomUser model with the customized admin class
admin.site.register(CustomUser, CustomUserAdmin)
