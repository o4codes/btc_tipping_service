import uuid
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch
from rest_framework_simplejwt.tokens import RefreshToken


# Create your tests here.
class UserCreateListTest(APITestCase):
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
            
    # test for creating a user
    @patch("api.utils.bitnob_customer_handler.BitnobCustomerHandler.create_customer")
    def test_create_user(self, mock_bitnob_customer_handler):
        """ Test for creating a user """

        client = APIClient()
        
        # create user
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "oforkansi.shadrach@gmail.com",
            "phone": "07068360667",
            "country_code": "+234",
            "password":"Oforshaddy1668"
        }
        
        mock_bitnob_customer_handler.return_value = {
                "id": "145",
                "firstName": "Test",
                "lastName": "User",
                "phone": "07068360667",
                "countryCode": "+234",
                "email": "oforkansi.shadrach@gmail.com"
            }    
            
        response = client.post("/api/v1/users", data, format="json")
        
        # get response body from response
        data = response.json()['data']
        
        assert response.status_code == 201
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert data["email"] == "oforkansi.shadrach@gmail.com"
        assert data['bitnob_id'] == "145"
    
    def test_create_user_with_missing_fields(self):
        """ Test for creating user with missing fields """
        client = APIClient()
        
        # create user
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "shadrach@gmail.com",
            "phone": "07068360667",
        }
        
        response = client.post("/api/v1/users", data, format="json")
        assert response.status_code == 400
    
    def test_list_users(self):
        """ Test for listing users """
        client = APIClient()
        
        # handle auth
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        response = client.get("/api/v1/users")
        print(response.status_code)
        assert response.status_code == 200 
        data = response.json()['data']
        assert type(data) == list
    
    
    def test_list_users_with_no_auth(self):
        """ Test for listing users with no auth """
        client = APIClient()
        
        response = client.get("/api/v1/users")
        assert response.status_code == 401
        
    def test_get_user_details(self):
        """ Test for getting user details """
        client = APIClient()
        
        # handle auth
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        response = client.get("/api/v1/users/{}".format(self.user.sec_id))
        print(response)
        assert response.status_code == 200 
        data = response.json()['data']
        assert type(data) == dict
        assert data["first_name"] == "Shaddy"
        assert data["last_name"] == "Tester"
        assert data['bitnob_id'] == "1"

    def test_get_user_details_with_no_auth(self):
        """ Test for getting user details with no auth """
        client = APIClient()
        
        response = client.get("/api/v1/users/{}".format(self.user.sec_id))
        assert response.status_code == 401
    
    def test_get_user_with_wrong_id(self):
        """ Test for getting user details with wrong id """
        client = APIClient()
        
        # handle auth
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        test_uuid = str(uuid.uuid4())
        response = client.get("/api/v1/users/{}".format(test_uuid))
        assert response.status_code == 404