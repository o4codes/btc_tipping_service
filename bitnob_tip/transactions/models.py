from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

class OnChainTransaction(models.Model):
    """
    Model for on-chain transactions.
    """
    btc_amount = models.FloatField(null=False, blank=False)
    satoshis_amount = models.IntegerField(null=True, blank=True)
    receiving_address = models.CharField(max_length=100, null=False, blank=False)
    sender = models.ForeognKey(get_user_model(), null=False, blank=False)
    description = models.CharField(max_length=100, null=False, blank=False)
    priority_level = models.CharField(max_length=100, null=False, blank=False)
    status= models.CharField(max_length=100, null=False, blank=False)
    bitnob_id = models.CharField(max_length=100, null=False, blank=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.sender.email}-{self.receiving_address}"
    
class LightningTransaction(models.Model):
    """
    Model for lightning transactions.
    """
    btc_amount = models.FloatField(null=False, blank=False)
    satoshis_amount = models.IntegerField(null=True, blank=True)
    lightening_address = models.CharField(max_length=100, null=False, blank=False)
    reference = models.CharField(max_length=100, null=False, blank=False)
    sender = models.ForeognKey(get_user_model(), null=False, blank=False)
    priority_level = models.CharField(max_length=100, null=False, blank=False)
    status= models.CharField(max_length=100, null=False, blank=False)
    bitnob_id = models.CharField(max_length=100, null=False, blank=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.sender.email}-{self.lightening_address}"
    
