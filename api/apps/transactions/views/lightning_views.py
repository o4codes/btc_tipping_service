from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q

from api.apps.transactions.serializers import LightningTransactionSerializer
from api.apps.transactions.models import OnChainTransaction, LightningTransaction
from api.utils.bitnob_lightning_handler import BtcLighteningHandler
from api.utils import schemas


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def validate_lightning_address(request, address):
    """ validates a lightning address
    """
    try:
        lightning_handler = BtcLighteningHandler()
        data = lightning_handler.verify_lightning_address(address)
        return Response(
            schemas.ResponseData.success(data), status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            schemas.ResponseData.error(str(e)), status=status.HTTP_400_BAD_REQUEST
        )
    

class LightningTransactionViews(APIView):
    queryset = OnChainTransaction.objects.all()
    serializer_class = LightningTransactionSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """ Create a new lightning transaction
        """
        serializer = LightningTransactionSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                schemas.ResponseData.success(serializer.data),
                status=status.HTTP_201_CREATED,
            )
        return Response(
            schemas.ResponseData.error(serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get(self, request, format=None):
        """ Gets all lightning transactions for logged in user
        """
        try:
            transactions = LightningTransaction.objects.filter(sender=request.user)
            
            serializer = LightningTransactionSerializer(transactions, many=True)
                
            return Response(
                schemas.ResponseData.success(serializer.data), status=status.HTTP_200_OK
            )
        except LightningTransaction.DoesNotExist as e:
            return Response(
                schemas.ResponseData.success([]), status=status.HTTP_200_OK
            )

class LightningDetailsView(APIView):
    queryset = LightningTransaction.objects.all()
    serializer_class = LightningTransactionSerializer
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, txid, format=None):
        """ Get details of a lightning transaction 
        """
        try:
            transaction = LightningTransaction.objects.get(Q(sec_id=txid) & Q(sender=request.user))
            
            if transaction.status == "pending":
                bitnob_lightening = BtcLighteningHandler()
                response = bitnob_lightening.get_transaction_data(transaction.bitnob_id) # retrieves details of trnsaction from bitnob
                if response["status"] == "success":
                    transaction.make_transaction()
                transaction.status = response['status']
                transaction.save() # updates status of transaction
                
            serializer = LightningTransactionSerializer(transaction)
                
            return Response(
                schemas.ResponseData.success(serializer.data), status=status.HTTP_200_OK
            )
        except LightningTransaction.DoesNotExist as e:
            return Response(
                schemas.ResponseData.error("Transaction does not exist"), status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                schemas.ResponseData.error(str(e)), status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["PUT"])
@permission_classes([AllowAny])
def receiver_confirm_btc(request, txid, address):
    """ Endpoint for receiver to confirm if payment is successful
    """
    try:
        transaction = LightningTransaction.objects.get(sec_id=txid, lnAddress=address)
        
        if transaction.status == "pending":
            bitnob_lightening = BtcLighteningHandler()
            response = bitnob_lightening.get_transaction_data(transaction.bitnob_id)
            transaction.status = response["status"]
            transaction.is_received = True
            transaction.save()
        
            data = {
                "message": "BTC payment confirmed",
            }
            return Response(
                schemas.ResponseData.success(data), status=status.HTTP_200_OK
            )
            
        elif transaction.status == "success":
            if transaction.is_received != True:
                transaction.is_received = True
                transaction.save()
                
                data = {"message": "BTC payment confirmed"}
                
                return Response(
                    schemas.ResponseData.success(data), status=status.HTTP_200_OK
                )
            
            data = {"message": "BTC payment already confirmed"}
                
            return Response(
                schemas.ResponseData.success(data), status=status.HTTP_200_OK
            )
            
        else:
            data = {"message": "BTC payment failed"}
            return Response(
                schemas.ResponseData.success(data), status=status.HTTP_200_OK
            )
    
    except LightningTransaction.DoesNotExist as e:
        return Response(
            schemas.ResponseData.error("Transaction does not exist"), status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            schemas.ResponseData.error(str(e)), status=status.HTTP_400_BAD_REQUEST
        )