from django.contrib import admin
from .models import Product, CompanySettings


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['reference', 'name', 'size', 'price', 'created_at']
    search_fields = ['reference', 'name']
    list_filter = ['created_at', 'size']
    readonly_fields = ['barcode_image', 'created_at', 'updated_at']


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number_1', 'phone_number_2']
