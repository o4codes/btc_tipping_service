from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from api.utils.bitnob_onchain_handler import BtcOnChainHandler
from api.apps.transactions.serializers import OnChainTransactionSerializer
from api.apps.transactions.models import OnChainTransaction, OnchainAddress
from api.utils import schemas


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generate_btc_address(request, email):
    """ Generates BTC address for the presently logged in user
    """
    try:
        user = get_user_model().objects.get(email=email)
        onchain_handler = BtcOnChainHandler()
        response = onchain_handler.generate_address(user.email)
        
        address_obj = OnchainAddress(user=user, address=response["address"])
        address_obj.save()
        
        data = {"email":email, "address": response["address"]}
        return Response(
            schemas.ResponseData.success(data), status=status.HTTP_200_OK
        )
    except get_user_model().DoesNotExist as e:
        return Response(
            schemas.ResponseData.error("User with email does not exist"), status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            schemas.ResponseData.error(str(e)), status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def validate_btc_onchain_address(request, address):
    """ Verifies if a bitcoin address is valid.
    """
    try:
        onchain_handler = BtcOnChainHandler()
        response = onchain_handler.verify_address(address)
        return Response(
            schemas.ResponseData.success({"message":"Address is valid"}), status=status.HTTP_200_OK
        )
    
    except ValueError as e:
        return Response(
            schemas.ResponseData.error(str(e)), status=status.HTTP_200_OK
        )
        
    except Exception as e:
        return Response(
            schemas.ResponseData.error(str(e)), status=status.HTTP_400_BAD_REQUEST
        )


# Create your views here.
class OnChainTransactionViews(APIView):
    queryset = OnChainTransaction.objects.all()
    serializer_class = OnChainTransactionSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = OnChainTransactionSerializer(
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
            transactions = OnChainTransaction.objects.get(sender=request.user)
            serializer = OnChainTransactionSerializer(transactions, many=True)
                
            return Response(
                schemas.ResponseData.success(serializer.data), status=status.HTTP_200_OK
            )
        except OnChainTransaction.DoesNotExist as e:
            return Response(
                schemas.ResponseData.success([]), status=status.HTTP_200_OK
            )


class OnChainTransactionDetailView(APIView):
    queryset = OnChainTransaction.objects.all()
    serializer_class = OnChainTransactionSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, sec_id, format=None):
        try:
            transaction = OnChainTransaction.objects.get(sec_id=sec_id, sender=request.user)
            serializer = OnChainTransactionSerializer(transaction)
            data = serializer.data

            if transaction.status == "pending":
                onchain_handler = BtcOnChainHandler()
                response = onchain_handler.get_transaction_data(data["bitnob_id"])
                data["status"] = response["status"]

                serializer = OnChainTransactionSerializer(
                    transaction, data=data, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    
            return Response(
                schemas.ResponseData.success(data), status=status.HTTP_200_OK
            )
        except OnChainTransaction.DoesNotExist as e:
            return Response(
                schemas.ResponseData.error("Transaction does not exist"), status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                schemas.ResponseData.error(str(e)), status=status.HTTP_400_BAD_REQUEST
            )

        
