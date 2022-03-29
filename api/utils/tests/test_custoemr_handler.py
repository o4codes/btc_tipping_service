import uuid
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch
from decouple import config
from api.utils.schemas import BitnobCustomer
from api.utils.bitnob_base import BitnobBase

class BitnobCustomerHandlerTest(APITestCase):
    """ This tests for creating and listing users 
    """

    def setUp(self):
        """ This sets up the test environment 
        """
        self.client = APIClient()
        self.customer = BitnobCustomer(
            firstName="test",
            lastName="tester",
            email="mail@mail.com",
            phone="07068360667",
            countryCode="+234",
        )
        
        self.base_url = "https://staging-api.flowertop.xyz"
        self.customer_endpoint = "/api/v1/customers"
        self.secret_key = config("BITNOB_SECRET_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
    @patch("api.utils.bitnob_customer_handler.BitnobCustomerHandler.create_customer.requests.post")
    def test_create_customer(self, mock_post):
        """ This tests for creating a customer 
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "status": "success",
            "data": {
                "id": str(uuid.uuid4()),
                "firstName": "test",
                "lastName": "tester",
                "email": "mail@mail.com",
                "phone":"07068360667",
                "countryCode":"+234",
            }
        }
        
        url = f"{self.base_url}{self.customer_endpoint}"
        response = self.client.post(url, data=self.customer.to_request_payload(), format="json", headers=self.headers)
        assert response.status_code == 200
        assert response.json()["data"]["firstName"] == "test"
    
    
    def test_create_customer_fail(self):
        """ This tests for creating a customer 
        """
        url = f"{self.base_url}{self.customer_endpoint}"
        data = self.customer.to_request_payload()
        del data['email']
        response = self.client.post(url, data=data, format="json", headers=self.headers)
        assert response.status_code == 400
        
        

        
    