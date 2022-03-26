from uuid import UUID
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.apps.users.models import User
from api.apps.users.serializers import UserSerializer
from api.apps.users.permissions import IsAuthenticatedOrCreate
from api.utils import schemas


class UserCreateList(APIView):
    """Handles creation of user and list all user
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrCreate,)

    def post(self, request, format=None):
        """Create a new user"""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            return Response(
                schemas.ResponseData.success(serializer.data), 
                status=status.HTTP_201_CREATED
                )
            
        return Response(
            schemas.ResponseData.error(serializer.errors), 
            status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request, format=None):
        """List all users"""
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(
            schemas.ResponseData.success(serializer.data), 
            status=status.HTTP_200_OK
        )

class UserDetail(APIView):
    """Handles retrieval of user"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrCreate,)

    def get(self, request, sec_id, format=None):
        """Retrieve a user
        """
        try:
            user = User.objects.get(sec_id=sec_id)
            serializer = UserSerializer(user)
            return Response(
                schemas.ResponseData.success(serializer.data), 
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist as e:
            return Response(
                schemas.ResponseData.error({"message": "User not found"}), 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                schemas.ResponseData.error(str(e)), 
                status=status.HTTP_400_BAD_REQUEST
            )
