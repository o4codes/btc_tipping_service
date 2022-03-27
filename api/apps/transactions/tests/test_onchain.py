import uuid
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch
from api.apps.transactions.models import OnChainTransaction
from rest_framework_simplejwt.tokens import RefreshToken

class OnChainTransactionTest(APITestCase):
    """ This tests for creating and listing users 
    """

    def setUp(self):
        """ This sets up the test environment 
        """
        self.user = get_user_model().objects.create_user(
            email="shaddy@gmail.com",
            first_name="Shaddy",
            last_name="Tester",
            password="testpassword",
            phone = "0712345678",
            country_code = "+234",
            bitnob_id = 1
        )
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token) 


    def test_valid_address(self):
        """ Test for valid address
        """
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        test_address = "2N3oefVeg6stiTb5Kh3ozCSkaqmx91FDbsm"
        response = client.get(f"/api/v1/btc/onchain/validate/{test_address}")
        assert response.status_code == 200
        assert response.json()['status'] == True
        
    def test_invalid_address(self):
        """ Test for invalid address
        """
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        test_address = "123rt"
        response = client.get(f"/api/v1/btc/onchain/validate/{test_address}")
        assert response.status_code == 200
        assert response.json()['status'] == False
        
    
    def test_address_validity_unauthorized(self):
        """ test for address validity without authorization
        """
        client = APIClient()
        
        test_address = "123rt"
        response = client.get(f"/api/v1/btc/onchain/validate/{test_address}")
        assert response.status_code == 401
    
    
    @patch("api.utils.bitnob_onchain_handler.BtcOnChainHandler.verify_address")
    @patch("api.utils.bitnob_onchain_handler.BtcOnChainHandler.send_onchain_btc")
    def test_payment_success(self, mock_send_onchain_btc, mock_verify_address):
        """ test for payment success
        """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        request_data = {
            "btc": "0.000000001",
            "receiving_address": "2N3oefVeg6stiTb5Kh3ozCSkaqmx91FDbsm",
            "description": "test payment"
        }
        
        mock_verify_address.return_value = True
        
        mock_send_onchain_btc.return_value = {
            "id": "1e258349-2043-4ca1-b39c-8418f9e0d36d",
            "status": "success",
            "address": "2N3oefVeg6stiTb5Kh3ozCSkaqmx91FDbsm",
            "satoshis": 0.000000001 * 100000000,
            "customerEmail": "mail@mail.com",
            "description": "test payment",
            "priorityLevel": "regular",
        }
        
        response = client.post(f"/api/v1/btc/onchain", data=request_data, format="json")
        data = response.json()['data']
        assert response.status_code == 201
        assert response.json()['status'] == True
        assert data['bitnob_id'] == "1e258349-2043-4ca1-b39c-8418f9e0d36d"