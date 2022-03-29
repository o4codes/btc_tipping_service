import hmac
from hashlib import sha512
from decouple import config
from django.shortcuts import redirect

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.apps.transactions.models import OnChainTransaction, LightningTransaction

@api_view(["GET"])
@permission_classes((AllowAny,))
def status_check(request):
    return Response({"message": "App is running"})


@api_view(["POST"])
@permission_classes((AllowAny,))
def webhook(request):
    secret = config("BITNOB_WEBHOOK_SECRET")
    signature = request.headers.get('x-bitnob-signature')
    computed_sig = hmac.new(
        key=secret.encode("utf-8"), msg=request.body, digestmod=sha512
    ).hexdigest()
    #Bitnob generated events will return True
    if signature == computed_sig:
        data = request.data
        event = data.get("event")
        
        if event == "btc.lightning.send.success":
            bitnob_id = data.get("data").get("id")
            transaction = LightningTransaction.objects.get(bitnob_id=bitnob_id)
            transaction.status = "success"
            transaction.save()
            
            transaction.make_transaction() # performs transaction
            
            # TODO: send a notification to the reciever on payment 
            return Response(status=status.HTTP_200_OK)
        
        if event == "btc.lightning.receive.success":
            return Response(status=status.HTTP_200_OK)
        
        if event == "btc.lightning.send.failed":
            bitnob_id = data.get("data").get("id")
            transaction = LightningTransaction.objects.get(bitnob_id=bitnob_id)
            transaction.status = "failed"
            transaction.save()
            
            # TODO: notify sender that payment failed
            return Response(status=status.HTTP_200_OK)
        
        if event == "btc.onchain.send.success":
            bitnob_id = data.get("data").get("id")
            transaction = OnChainTransaction.objects.get(bitnob_id=bitnob_id)
            transaction.status = "success"
            transaction.save()

            transaction.make_transaction() # performs transaction
                        
            # TODO: notify receiver on payment
            return Response(status=status.HTTP_200_OK)
        
        if event == "btc.onchain.receive.success":
            return Response(status=status.HTTP_200_OK)
            
        if event == "btc.onchain.send.failed":
            bitnob_id = data.get("data").get("id")
            transaction = OnChainTransaction.objects.get(bitnob_id=bitnob_id)
            transaction.status = "failed"
            transaction.save()
            
            # TODO: notify sender that payment failed
            return Response(status=status.HTTP_200_OK)
              
    return Response(status=status.HTTP_200_OK)
    