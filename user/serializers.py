from rest_framework import serializers
from .models import Address, User, CustomerProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        token["mobile_number"] = user.mobile_number
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["role"] = self.user.role
        data["username"] = self.user.username
        data["mobile_number"] = self.user.mobile_number
        return data

class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)
    mobile_number = serializers.CharField(required=True, max_length=15)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'mobile_number']

    def validate_mobile_number(self, value):
        if User.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError("This mobile number is already registered.")
        return value

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='customer',
            mobile_number=validated_data['mobile_number']
        )
        user.set_password(validated_data['password'])
        user.save()

        CustomerProfile.objects.create(user=user)
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "address_line",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default",
            "latitude",
            "longitude",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data.pop("user", None)
        return Address.objects.create(user=user, **validated_data)