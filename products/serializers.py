from rest_framework import serializers
from .models import Category, Product, ProductImage

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'vendor', 'name', 'description', 'price', 'stock', 'category', 'created_at', 'updated_at')
        read_only_fields = ('vendor', 'created_at', 'updated_at')

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'product', 'image', 'alt_text', 'created_at')

class MultipleImageUploadSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField()
    )

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'parent', 'created_at')