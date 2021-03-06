from django.dispatch import receiver
from rest_framework import serializers
from django.contrib.auth import get_user_model
from api.utils.bitnob_onchain_handler import BtcOnChainHandler
from api.utils.bitnob_lightning_handler import BtcLighteningHandler
from api.utils import schemas

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

    def validate(self, data):
        """ validate serializer
        """
        
        receiving_address = data.get("receiving_address")
        onchain_handler = BtcOnChainHandler()
        try:
            onchain_handler.verify_address(receiving_address) # checks if address is valid
        except Exception as e:
            raise serializers.ValidationError(schemas.ResponseData.error(e))
        
        return data
        
    
    def create(self, validated_data):
        """
        Create a new on-chain transaction.
        """
        
        sender = self.context["request"].user
        satoshis = validated_data.get("btc") * 100000000
        
        # intialize payment object
        payment_object = schemas.BtcOnChainPayment(
            btc_amount=validated_data["btc"],
            address=validated_data["receiving_address"],
            customer_email=self.context["request"].user.email,
            description=validated_data.get("description"),
        )

        try:
            if sender.satoshis <= satoshis:
                raise serializers.ValidationError(schemas.ResponseData.error("Inadequate Satoshis to send"))
            
            # gets user assigned to the receiving address
            onchain_handler = BtcOnChainHandler()
            onchain_handler.verify_address(validated_data["receiving_address"])
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

            on_chain_transaction.save() # save transaction
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
            "lnAddress",
            "satoshis",
            "reference",
            "description",
            "sender",
            "status",
            "bitnob_id",
            "is_received",
            "created_at",
            "updated_at",
        )
        
        read_only_fields = (
            "bitnob_id",
            "satoshis",
            "status",
            "reference",
            "sender",
            "is_received",
            "created_at",
            "updated_at",
            
        )
        
    
    def create(self, validated_data):
        """
        Create a new lightening transaction.
        """
        
        sender = self.context["request"].user
        
        if sender.satoshis <= validated_data["btc"] * 100000000: # check if sender has enough satoshis
            raise serializers.ValidationError("Sender does not have enough satoshis")
        
        # intialize payment object
        payment_object = schemas.BtcLightningPayment(
            btc_amount=validated_data["btc"],
            description=validated_data["description"],
            sender_email=self.context["request"].user.email,
            ln_address=validated_data["lnAddress"],
        )
        
        try:
            lightning_handler = BtcLighteningHandler()
            response = lightning_handler.pay_lightning_address(payment_object) # perform lightning payment
            # response = payment_object.to_response_payload()
            
            lightening_transaction = LightningTransaction.objects.create(
                btc = validated_data["btc"],
                satoshis = response["satoshis"],
                reference = response["reference"],
                sender = self.context["request"].user,
                lnAddress = response["lnAddress"],
                status = response["status"],
                bitnob_id = response["id"],
                description = validated_data["description"]
            )
            
            lightening_transaction.save() # save transaction
            
            return lightening_transaction
        except Exception as e:
            # raise e
            raise serializers.ValidationError(schemas.ResponseData.error(e))
        