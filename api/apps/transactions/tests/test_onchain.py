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

        self.transaction = OnChainTransaction.objects.create(
            sec_id = uuid.uuid4(),
            btc = "0.000000001",
            satoshis = 100000000,
            receiving_address = "2N3oefVeg6stiTb5Kh3ozCSkaqmx91FDbsm",
            sender = self.user,
            description = "test payment",
            priority_level = "regular",
            bitnob_id = 1,
            status = "success"
        )
        self.transaction.save()

    @patch("api.utils.bitnob_onchain_handler.BtcOnChainHandler.verify_address")
    def test_valid_address(self, mock_verify_address):
        """ Test for valid address
        """
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        mock_verify_address.return_value = True
        
        test_address = "2N3oefVeg6stiTb5Kh3ozCSkaqmx91FDbsm"
        response = client.get(f"/api/v1/btc/onchain/validate/{test_address}")
        assert response.status_code == 200
        assert response.json()['status'] == True
    
    @patch("api.utils.bitnob_onchain_handler.BtcOnChainHandler.verify_address")
    def test_invalid_address(self, mock_verify_address):
        """ Test for invalid address
        """
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        mock_verify_address.side_effect = ValueError("Invalid address")
        
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
        
    
    @patch("api.utils.bitnob_onchain_handler.BtcOnChainHandler.verify_address")
    @patch("api.utils.bitnob_onchain_handler.BtcOnChainHandler.send_onchain_btc")
    def test_payment_unauthorised(self, mock_send_onchain_btc, mock_verify_address):
        """ test for payment success
        """
        client = APIClient()
    
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
        assert response.status_code == 401
    
    @patch("api.utils.bitnob_onchain_handler.BtcOnChainHandler.verify_address")
    def test_payment_invalid_address(self, mock_verify_address):
        """ test for payment success
        """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        request_data = {
            "btc": "0.000000001",
            "receiving_address": "123rt",
            "description": "test payment"
        }
        
        mock_verify_address.side_effect = ValueError("Invalid address")
        
        response = client.post(f"/api/v1/btc/onchain", data=request_data, format="json")
        assert response.status_code == 400
        assert response.json()['status'] == False
        
    
    def test_receiver_confirm_tranaction_success(self):
        """ test for receiver confirm transaction
        """
        
        client = APIClient()
        txid = self.transaction.sec_id
        address = self.transaction.receiving_address
        response = client.put(f"/api/v1/btc/onchain/transactions/{txid}/address/{address}")
        assert response.status_code == 200
        
    def test_receiver_confirm_transaction_fail(self):
        """ test for receiver confirm transaction failure
        """
        
        client = APIClient()
        txid = "123rt"
        address = "234rt"
        response = client.put(f"/api/v1/btc/onchain/transactions/{txid}/address/{address}")
        assert response.status_code == 400
        