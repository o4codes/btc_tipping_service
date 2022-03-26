from django.dispatch import receiver
from rest_framework import serializers
from django.contrib.auth import get_user_model
from utils.bitnob_onchain_handler import BtcOnChainHandler
from bitnob_tip.utils.bitnob_lightning_handler import BtcLighteningHandler
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
    receiver_email = serializers.EmailField(write_only=True)
    class Meta:
        model = LightningTransaction
        fields = (
            "id",
            "btc",
            "satoshis",
            "reference",
            "description",
            "sender",
            "receiver_email",
            'receiver',
            "status",
            "bitnob_id",
            "is_receiver_confirmed",
            "created_at",
            "updated_at",
        )
        
        read_only_fields = (
            "bitnob_id",
            "satoshis",
            "status",
            'receiver',
            "reference",
            "sender",
            "is_receiver_confirmed",
            "created_at",
            "updated_at",
            
        )
        
        write_only_fields = ("receiver_email",)
    
    def validate(self, data):
        """
        Validate the data.
        """
        if get_user_model().objects.filter(email=data["receiver_email"]).count() == 0:
            raise serializers.ValidationError("Reciever account does not exist")
        
        return data
    
    def create(self, validated_data):
        """
        Create a new lightening transaction.
        """
        
        sender = self.context["request"].user
        receiver = get_user_model().objects.get(email=validated_data["receiver_email"])
        
        if sender.email == validated_data["receiver_email"]: # if sender and receiver are same
            raise serializers.ValidationError("Sender and receiver cannot be the same")
        
        if sender.satoshis <= validated_data["btc"] * 100000000: # check if sender has enough satoshis
            raise serializers.ValidationError("Sender does not have enough satoshis")
        
        # intialize payment object
        payment_object = schemas.BtcLightningPayment(
            btc_amount=validated_data["btc"],
            description=validated_data["description"],
            sender_email=self.context["request"].user.email,
            receiver_email=validated_data["receiver_email"]
        )
        
        
        try:
            lightning_handler = BtcLighteningHandler()
            payment_object = lightning_handler.create_invoice(payment_object)
            payment_object = lightning_handler.pay_invoice(payment_object)
            response = payment_object.to_response_payload()
            
            lightening_transaction = LightningTransaction.objects.create(
                btc = validated_data["btc"],
                satoshis = response["satoshis"],
                reference = response["reference"],
                sender = self.context["request"].user,
                receiver = get_user_model().objects.get(email=validated_data["receiver_email"]),
                status = response["status"],
                payment_request = response["request"],
                bitnob_id = response["id"],
            )
            
            validated_data.pop("receiver_email")
            
            lightening_transaction.save()
            lightening_transaction.make_transaction() # performs transactions
            
            return lightening_transaction
        except Exception as e:
            # raise e
            raise serializers.ValidationError(schemas.ResponseData.error(e))
        