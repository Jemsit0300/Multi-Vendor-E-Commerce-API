from rest_framework import serializers
from .models import User
from vendors.models import Vendor

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')

    def create(self, validated_data):
        email = validated_data.get('email')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=email,
            password=validated_data['password'],
            role=validated_data['role']
        )
        
        if user.role == "vendor":
            Vendor.objects.create(
                user=user,
                store_name="My Store"
            )

        if email is None:
            user.email = None
            user.save(update_fields=['email'])
        return user