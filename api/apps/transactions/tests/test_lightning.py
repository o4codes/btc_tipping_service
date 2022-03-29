import uuid
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch
from api.apps.transactions.models import LightningTransaction
from rest_framework_simplejwt.tokens import RefreshToken
# Create your tests here.

class LightningTransactionTest(APITestCase):
    """ This tests for creating and listing users 
    """

    def setUp(self):
        """ This sets up the test environment 
        """
        # setup user
        self.user = get_user_model().objects.create_user(
            email="shaddy@gmail.com",
            first_name="Shaddy",
            last_name="Tester",
            password="testpassword",
            phone = "0712345678",
            country_code = "+234",
            bitnob_id = 1
        )
        
        # set up the refresh token
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        
        #setup transaction
        self.transaction = LightningTransaction.objects.create(
            sec_id = uuid.uuid4(),
            btc = 0.00000001,
            satoshis = 100000000,
            sender = self.user,
            lnAddress = "bernard@bitnob.com",
            reference = str(uuid.uuid4()),
            status = "success",
            description = "Payments",
            bitnob_id = 1,
            is_received = False
        )
        self.transaction.save()
        
        
    @patch("api.utils.bitnob_lightning_handler.BtcLighteningHandler.verify_lightning_address")
    def test_valid_address(self, mock_verify_address):
        """ Test for valid address
        """
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        mock_verify_address.return_value = {
            "image": "",
            "identifier": "fiatjaf@dollar.lol",
            "description": "Satoshis to fiatjaf@dollar.lol.",
            "callback": "https://dollar.lol/.well-known/lnurlp/fiatjaf",
            "commentAllowed": 0,
            "satMinSendable": 1,
            "satMaxSendable": 100000
        }
        
        
        test_address = "bernard@bitnob.com"
        response = client.get(f"/api/v1/btc/lightning/validate/{test_address}")
        assert response.status_code == 200
        
    
    @patch("api.utils.bitnob_lightning_handler.BtcLighteningHandler.verify_lightning_address")
    def test_invalid_address(self, mock_verify_address):
        """ Test for valid address
        """
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        mock_verify_address.side_effect = Exception("LnAddress not valid")
        
        test_address = "sheddy@something.com"
        response = client.get(f"/api/v1/btc/lightning/validate/{test_address}")
        assert response.status_code == 400
        
    def test_verify_address_unauthorized(self):
        """ Test for valid address
        """
        
        client = APIClient()
        response = client.get(f"/api/v1/btc/lightning/validate/{self.transaction.lnAddress}")
        assert response.status_code == 401
    
    
    @patch("api.utils.bitnob_lightning_handler.BtcLighteningHandler.verify_lightning_address")
    @patch("api.utils.bitnob_lightning_handler.BtcLighteningHandler.pay_lightning_address")
    def test_payment_success(self, mock_pay_address, mock_verify_address):
        """ Test for valid address
        """
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        mock_pay_address.return_value = {
            "id": str(uuid.uuid4()),
            "btc": 0.000000003,
            "satoshis": 300000000,
            "sender": self.user,
            "lnAddress": self.transaction.lnAddress,
            "reference": str(uuid.uuid4()),
            "status": "success",
            "description": "Payments",
            "bitnob_id": "pay123",
        }
        
        mock_verify_address.return_value = {
            "image": "",
            "identifier": self.transaction.lnAddress,
            "description": "Satoshis to fiatjaf@dollar.lol.",
            "callback": "https://dollar.lol/.well-known/lnurlp/fiatjaf",
            "commentAllowed": 0,
            "satMinSendable": 1,
            "satMaxSendable": 100000
        }
        
        request_payload = {
            "lnAddress": self.transaction.lnAddress,
            "btc": 0.000000003,
            "description": "Payments",
        }
        
        response = client.post(f"/api/v1/btc/lightning", request_payload)
        assert response.status_code == 201
        
    
    def test_payment_unauthorised(self):
        """ Test for unauthorised payment
        """
        request_payload = {
            "lnAddress": self.transaction.lnAddress,
            "btc": 0.000000003,
            "description": "Payments",
        }
        
        client = APIClient()
        response = client.post(f"/api/v1/btc/lightning", request_payload)
        assert response.status_code == 401
        
    @patch("api.utils.bitnob_lightning_handler.BtcLighteningHandler.verify_lightning_address")
    def test_invalid_address_payment(self, mock_verify_address):
        """ Test for valid address
        """
        
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        mock_verify_address.side_effect = Exception("LnAddress not valid")
        
        request_payload = {
            "lnAddress": self.transaction.lnAddress,
            "btc": 0.000000003,
            "description": "Payments",
        }
        
        response = client.post(f"/api/v1/btc/lightning", request_payload)
        assert response.status_code == 400
        
    
    def test_receiver_confirm_success(self):
        """ Test for receiver confirm success
        """
        client = APIClient()
        response = client.put(f"/api/v1/btc/lightning/transactions/{self.transaction.sec_id}/address/{self.transaction.lnAddress}")
        assert response.status_code == 200
        
    def test_receiver_confirm_fail(self):
        """ Test for receiver confirm with wrong address and transaction id
        """
        client = APIClient()
        txid = "123456789"
        address = "123456789"
        response = client.put(f"/api/v1/btc/lightning/transactions/{txid}/address/{address}")
        assert response.status_code == 400
    
    def test_list_transactions(self):
        """ Test for list all transactions
        """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        response = client.get("/api/v1/btc/lightning")
        assert response.status_code == 200
        assert type(response.json()['data']) == list
        
    def test_get_transaction(self):
        """ Test to get a transaction
        """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        response = client.get(f"/api/v1/btc/lightning/{self.transaction.sec_id}")
        assert response.status_code == 200
        assert response.json()['data']['id'] == str(self.transaction.sec_id)