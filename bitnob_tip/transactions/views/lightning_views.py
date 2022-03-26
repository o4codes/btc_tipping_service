from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q

from transactions.serializers import LightningTransactionSerializer
from transactions.models import OnChainTransaction, LightningTransaction
from utils.bitnob_lightening_handler import BtcLighteningHandler
from utils import schemas

class LightningTransactionViews(APIView):
    queryset = OnChainTransaction.objects.all()
    serializer_class = LightningTransactionSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
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
        try:
            transactions = LightningTransaction.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
            
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
    
    def get(self, request, sec_id, format=None):
        """ Get details of a lightning transaction 
        """
        try:
            transactions = LightningTransaction.objects.filter(Q(sec_id=sec_id) & (Q(sender=request.user) | Q(receiver=request.user)))
            
            # transaction = LightningTransaction.objects.get(sec_id=sec_id, sender=request.user)
            serializer = LightningTransactionSerializer(transactions, many=True)
            data = serializer.data
            
            if data == []:
                raise LightningTransaction.DoesNotExist
            
            if data[0]['status'] == "pending":
                bitnob_lightening = BtcLighteningHandler()
                response = bitnob_lightening.get_transaction_data(data[0]["bitnob_id"])
                transactions[0].status = response['status']
                transactions[0].save()
                
            return Response(
                schemas.ResponseData.success(data[0]), status=status.HTTP_200_OK
            )
        except LightningTransaction.DoesNotExist as e:
            return Response(
                schemas.ResponseData.error("Transaction does not exist"), status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                schemas.ResponseData.error(str(e)), status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated,])
def receiver_confirm_btc(request, sec_id):
    """ Endpoint for receiver to confirm if payment is successful
    """
    try:
        transaction = LightningTransaction.objects.get(sec_id=sec_id, receiver=request.user)
        
        if transaction.status == "pending":
            bitnob_lightening = BtcLighteningHandler()
            response = bitnob_lightening.get_transaction_data(transaction.bitnob_id)
            transaction.status = response["status"]
            transaction.is_receiver_confirmed = True
            transaction.save()
        
            data = {
                "message": "BTC payment confirmed",
            }
            return Response(
                schemas.ResponseData.success(data), status=status.HTTP_200_OK
            )
            
        elif transaction.status == "success":
            if transaction.is_receiver_confirmed != True:
                transaction.is_receiver_confirmed = True
                transaction.save()
                
                data = {
                    "message": "BTC payment confirmed",
                }
                
                return Response(
                    schemas.ResponseData.success(data), status=status.HTTP_200_OK
                )
            
            data = {
                    "message": "BTC payment already confirmed",
                }
                
            return Response(
                schemas.ResponseData.success(data), status=status.HTTP_200_OK
            )
            
        else:
            data = {
                "message": "BTC payment failed",
            }
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