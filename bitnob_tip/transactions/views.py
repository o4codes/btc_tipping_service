from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, get_list_or_404

from .serializers import OnChainTransactionSerializer
from .models import OnChainTransaction
from utils import schemas
from utils.bitnob_handler import BitnobHandler

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
                bitnob_handler = BitnobHandler()
                response = bitnob_handler.get_transaction_data(data["bitnob_id"])
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
