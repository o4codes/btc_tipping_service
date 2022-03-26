from rest_framework import serializers
from django.contrib.auth import get_user_model
import phonenumbers

from utils.bitnob_customer_handler import BitnobCustomerHandler
from utils.schemas import BitnobCustomer


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True, source="sec_id")
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "bitnob_id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "country_code",
            "password",
        )
        read_only_fields = ("id", "bitnob_id")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        country_code = data.get("country_code")
        phone = data.get("phone")
        phone = phone if phone[0] != "0" else phone[1:]
        full_phone_number = f"{country_code}{phone}"
        if phonenumbers.is_valid_number(phonenumbers.parse(full_phone_number)):
            return data
        raise serializers.ValidationError("Invalid country code")

    def create(self, validated_data):

        # create user as bitnob customer
        customer = BitnobCustomer(
            firstName=validated_data.get("first_name"),
            lastName=validated_data.get("last_name"),
            phone=validated_data.get("phone"),
            countryCode=validated_data.get("country_code"),
            email=validated_data.get("email"),
        )

        try:
            bitnob_response = BitnobCustomerHandler().create_customer(customer)

            validated_data["bitnob_id"] = bitnob_response["id"]
            user = get_user_model().objects.create_user(**validated_data)
            return user

        except Exception as e:
            raise serializers.ValidationError(e)
