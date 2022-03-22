import requests
from pydantic import BaseModel
from decouple import config

class BitnobCustomer(BaseModel):
    """ Serves as schema for customer data """
    id: str = None
    first_name: str
    last_name: str
    email: str
    phone: str
    country_code: str

class BitnobHandler:
    """ class handles all requests to the Bitnob API
    """
    
    def __init__(self) -> None:
        self.__base_url = 'https://sandboxapi.bitnob.co'
        self.__customer_endpoint = '/api/v1/customers'
        self.__secret_key = config('BITNOB_SECRET_KEY')
        self.__public_key = config('BITNOB_PUBLIC_KEY')
        
    def create_customer(self, customer_data: BitnobCustomer) -> dict:
        """ creates a customer in Bitnob
        
        Args:
            customer_data (BitnobCustomer): customer data
        
        Returns:
            dict: response from Bitnob
            
        Raises:
            Exception: if request fails
        """
        
        url = f"{self.__base_url}{self.__customer_endpoint}"
        
        headers = {
            'Authorization': f'Bearer {self.__secret_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        customer_data = customer_data.dict()
        customer_data['country_code'] = customer_data['country_code'].replace('+', '')
        response = requests.post(url, json=customer_data, headers=headers)
        
        if response.status_code == 200:
            return response.json()['data']
        
        raise Exception(f"Error creating customer: {response.json()['message']}")
    