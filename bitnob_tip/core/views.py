import hmac
from hashlib import sha512
import os

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes((AllowAny,))
def status_check(request):
    return Response({"message": "App is running"})

@api_view(["POSY"])
@permission_classes((AllowAny,))
def webhook(request):
    secret = os.environ.get("BITNOB_WEBHOOK_SECRET")
    signature = request.headers.get('x-bitnob-signature')
    computed_sig = hmac.new(
        key=secret.encode("utf-8"), msg=request.body, digestmod=sha512
    ).hexdigest()
    #Bitnob generated events will return True
    if signature == computed_sig:
        # TODO: Handle event
        return Response(data={"message": "Event received"}, status=status.HTTP_200_OK)
    
