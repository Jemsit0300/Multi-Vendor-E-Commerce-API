from rest_framework import serializers
from django.db.models import Avg
from .models import Category, Product, ProductImage

class ProductSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'vendor', 'name', 'description', 'price', 'stock', 'category', 'avg_rating', 'created_at', 'updated_at')
        read_only_fields = ('vendor', 'created_at', 'updated_at')

    def get_avg_rating(self, obj):
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 2) if avg is not None else None

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