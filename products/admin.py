from django.contrib import admin
from .models import Product, ProductImage, Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price', 'stock', 'category', 'created_at')
    list_filter = ('vendor', 'category', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',) 

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('alt_text',)
    ordering = ('-created_at',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):      
    list_display = ('name', 'slug', 'parent', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'slug')
    ordering = ('-created_at',)
    