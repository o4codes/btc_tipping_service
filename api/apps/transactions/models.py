import uuid
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.


class OnChainTransaction(models.Model):
    """
    Model for on-chain transactions.
    """
    sec_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    btc = models.FloatField(null=False, blank=False)
    satoshis = models.IntegerField(null=True, blank=True)
    receiving_address = models.CharField(max_length=100, null=False, blank=False)
    sender = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=False, blank=False, related_name="onchain_sender",
    )
    receiver = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=False, blank=False, related_name="onchain_receiver",
    )
    description = models.CharField(max_length=100, null=False, blank=False)
    priority_level = models.CharField(max_length=100, null=False, blank=False)
    status = models.CharField(max_length=100, null=False, blank=False)
    bitnob_id = models.CharField(max_length=100, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_received = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.email}-{self.receiving_address}"


class LightningTransaction(models.Model):
    """
    Model for lightning transactions.
    """
    sec_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    btc = models.FloatField(null=False, blank=False)
    satoshis = models.IntegerField(null=True, blank=True)
    reference = models.CharField(max_length=100, null=False, blank=False)
    sender = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=False, blank=False, related_name="lightening_sender"
    )
    receiver = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=False, blank=False, related_name="lightening_receiver"
    )
    status = models.CharField(max_length=100, null=False, blank=False)
    description = models.CharField(max_length=100, null=False, blank=False, default="Payments")
    bitnob_id = models.CharField(max_length=100, null=False, blank=False)
    payment_request = models.CharField(max_length=100, null=False, blank=False)
    is_received = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender.email}-{self.lightening_address}"

    def make_transaction(self):
        """
        Make a lightning transaction.
        """
        self.sender.deduct_satoshis(self.satoshis)
        self.receiver.add_satoshis(self.satoshis)
        return 