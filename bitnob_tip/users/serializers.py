from rest_framework import serializers
from django.contrib.auth import get_user_model
import phonenumbers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'bitnob_id', 'email', 'first_name', 'last_name', 'phone', 'country_code', 'password')
        read_only_fields = ('id', 'bitnob_id')
        extra_kwargs = {'password': {'write_only': True}}
        
    def validate(self, data):
        country_code = data.get('country_code')
        phone = data.get('phone')
        if phonenumbers.is_valid_number(phonenumbers.parse(phone, country_code)):
            return data
        raise serializers.ValidationError('Invalid country code')
    
    def create(self, validated_data):
        pass
