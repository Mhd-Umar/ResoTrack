from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User, Lab, Resource, Complaint, Suggestion, Stock

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    fieldsets = DefaultUserAdmin.fieldsets + (
        (None, {'fields': ('role', 'department', 'status')}),
    )

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ('lab_name', 'department', 'lab_code', 'lab_admin')

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('resource_name', 'lab', 'status', 'last_updated')
    list_filter = ('status', 'lab')

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('user', 'lab', 'priority', 'status', 'date')
    list_filter = ('status', 'priority', 'lab')

@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'status', 'date_submitted')
    list_filter = ('status', 'category')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('stock_name', 'lab', 'date', 'price')
    list_filter = ('lab',)
