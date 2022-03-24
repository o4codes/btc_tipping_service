from rest_framework import serializers
from django.contrib.auth import get_user_model
from utils.bitnob_handler import BtcOnChainHandler
from utils import schemas

from .models import OnChainTransaction, LightningTransaction


class OnChainTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for on-chain transactions.
    """
    id = serializers.UUIDField(read_only=True, source="sec_id")
    class Meta:
        model = OnChainTransaction
        fields = (
            "id",
            "btc",
            "satoshis",
            "receiving_address",
            "sender",
            "description",
            "priority_level",
            "status",
            "bitnob_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "bitnob_id",
            "satoshis",
            "status",
            "sender",
            "priority_level",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        """
        Create a new on-chain transaction.
        """
        # intialize payment object
        payment_object = schemas.BtcOnChainPayment(
            btc_amount=validated_data["btc"],
            address=validated_data["receiving_address"],
            customer_email=self.context["request"].user.email,
            description=validated_data["description"],
        )

        try:
            onchain_handler = BtcOnChainHandler()
            response = onchain_handler.send_onchain_btc(
                payment_object
            )  # perform on-chain payment

            on_chain_transaction = OnChainTransaction.objects.create(
                bitnob_id=response["id"],
                btc=validated_data["btc"],
                satoshis=response["satoshis"],
                receiving_address=response["address"],
                sender=self.context["request"].user,
                description=validated_data["description"],
                priority_level=response["priorityLevel"],
                status=response["status"],
            )

            on_chain_transaction.save()
            return on_chain_transaction

        except Exception as e:
            raise serializers.ValidationError(schemas.ResponseData.error(e))


class LightningTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for lightning transactions.
    """
    id = serializers.UUIDField(read_only=True, source="sec_id")
    
    class Meta:
        model = LightningTransaction
        fields = (
            "id",
            "btc",
            "satoshis",
            "lightening_address",
            "reference",
            "sender",
            "status",
            "bitnob_id",
            "created_at",
            "updated_at",
        )
        
        read_only_fields = (
            "bitnob_id",
            "satoshis",
            "status",
            "sender",
            "created_at",
            "updated_at",
        )
    
    def create(self, validated_data):
        """
        Create a new lightening transaction.
        """
        
        # intialize payment object
        payment_object = schemas.BtcLightningPayment(
            btc_amount=validated_data["btc"],
            lnAddress=validated_data["lightening_address"],
            reference=validated_data["reference"],
            customer_email=self.context["request"].user.email,
        )
        
        try:
            bitnob_handler = BitnobHandler()
            response = bitnob_handler.send_lightning_payment(payment_object)
            print(response)
            
            lightening_transaction = LightningTransaction.objects.create(
                btc = validated_data["btc"],
            )
        except Exception as e:
            pass