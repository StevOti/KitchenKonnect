from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
	"""Register CustomUser with default UserAdmin plus extra fields."""
	fieldsets = UserAdmin.fieldsets + (
		('Extra', {'fields': ('role', 'admin_level', 'dietary_preferences', 'bio')}),
	)

	list_display = UserAdmin.list_display + ('role', 'admin_level')
