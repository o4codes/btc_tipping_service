from urllib.error import HTTPError
from decouple import config
import requests

from api.utils.schemas import BitnobCustomer
from api.utils.bitnob_base import BitnobBase

class BitnobCustomerHandler(BitnobBase):
    """class handles all requests to the Bitnob CustomerAPI
    """

    def __init__(self) -> None:
        super().__init__()
        self.__customer_endpoint = "/api/v1/customers"

    def create_customer(self, customer: BitnobCustomer) -> dict:
        """creates a customer in Bitnob

        Args:
            customer_data (BitnobCustomer): customer data to be created in Bitnob
            sample_data:
                'firstName': 'John',
                'lastName': 'Doe',
                'email': 'johndoe@mail.com',
                'phone': '1234567890',
                'countryCode': '+234'


        Returns:
            dict: response from Bitnob
            sample_data: {
                "firstName": "Gabby",
                "lastName": "Precious",
                "email": "gabby@bitnob.com",
                "phone": "9021534385",
                "countryCode": "+234",
                "blacklist": false,
                "id": "1e258349-2043-4ca1-b39c-8418f9e0d36d",
                "createdAt": "2021-08-26T11:15:23.788Z",
                "updatedAt": "2021-08-26T11:15:23.788Z"
            }

        Raises:
            Exception: if request fails
            Exception: if connection fails
        """

        url = f"{self.base_url}{self.__customer_endpoint}"

        data = customer.to_request_payload()

        try:
            response = requests.post(url, json=data, headers=self.headers)

            if response.status_code == 200:
                return response.json()["data"]

            raise Exception(f"Creation Error: {response.json()['message']}")

        except (HTTPError, ConnectionError) as e:
            raise Exception(f"Request Failed due to: {e}")