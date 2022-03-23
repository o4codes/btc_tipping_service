import requests
from decouple import config

class BitnobHandler:
    """ class handles all requests to the Bitnob API
    """
    
    def __init__(self) -> None:
        self.__base_url = 'https://sandboxapi.bitnob.co'
        self.__customer_endpoint = '/api/v1/customers'
        self.__secret_key = config('BITNOB_SECRET_KEY')
        self.__public_key = config('BITNOB_PUBLIC_KEY')
        
    def create_customer(self, **customer_data) -> dict:
        """ creates a customer in Bitnob
        
        Args:
            customer_data (dict): customer data to be created in Bitnob
            sample_data: {
                'firstName': 'John',
                'lastName': 'Doe',
                'email': 'johndoe@mail.com',
                'phone': '1234567890',
                'countryCode': '+234'
            }
        
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
        """
        
        url = f"{self.__base_url}{self.__customer_endpoint}"
        
        headers = {
            'Authorization': f'Bearer {self.__secret_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.post(url, json=customer_data, headers=headers)
        
        if response.status_code == 200:
            return response.json()['data']
        
        raise Exception(f"Error creating customer: {response.json()['message']}")
    