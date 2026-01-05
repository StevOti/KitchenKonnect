from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'admin_level',
        )
        read_only_fields = ('role', 'admin_level')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        # registration should not allow arbitrary role assignment; users
        # register as regular users by default.
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'admin_level')

    def validate_role(self, value):
        allowed = [c[0] for c in getattr(User, 'ROLE_CHOICES', [])]
        if value not in allowed:
            raise serializers.ValidationError('Invalid role')
        return value

    def update(self, instance, validated_data):
        # Only allow updating role and admin_level via this serializer
        role = validated_data.get('role')
        level = validated_data.get('admin_level')
        if role is not None:
            instance.role = role
        if level is not None:
            try:
                instance.admin_level = int(level)
            except Exception:
                instance.admin_level = 0
        instance.save()
        return instance
