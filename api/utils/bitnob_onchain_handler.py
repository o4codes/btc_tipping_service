from urllib.error import HTTPError
import requests
from decouple import config
from api.utils.schemas import BtcOnChainPayment
from api.utils.bitnob_base import BitnobBase


class BtcOnChainHandler(BitnobBase):
    """ class handles onchain btc payment 
    """
    def __init__(self):
        super().__init__()
        self.__onchain_btc_endpoint = "/api/v1/wallets/send_bitcoin"
        self.__transactions_endpoint = "/api/v1/transactions"
        self.__generate_address_endpoint = "/api/v1/addresses/generate"
        self.__verify_btc_onchain = "/api/v1/addresses/validate"

    def verify_address(self, address) -> bool:
        """ Verifies if btc address is valid
        Args:
            address (str): btc address to be verified
            
        Returns:
            bool: True if address is valid, False otherwise
            
        Raises:
            Exception: if request fails or if address is not found
        """
        url = f"{self.base_url}{self.__verify_btc_onchain}/{address}"
        try:
            response = requests.request("GET", url, headers=self.headers)
            if response.status_code == 200 and response.json().get("data").get("isvalid"):
                return True
            raise ValueError("Invalid Address")
        except (HTTPError, ConnectionError) as e:
            raise Exception("Request Failed due to "+str(e))
    
    
    def generate_address(self, customerEmail) -> str:
        """generates new address for customer
        
        Args:
            customerEmail (str): email of customer
        
        Returns:
            str: new address
            
        Raises:
            Exception: if request fails
        """
        url = f"{self.base_url}{self.__generate_address_endpoint}"
        data = {"customerEmail": customerEmail}
        try:
            response = requests.request("POST", url, headers=self.headers, json=data)
            if response.status_code == 200:
                return response.json().get("data").get("address")
            raise Exception("Invalid Address")
        except (HTTPError, ConnectionError) as e:
            raise Exception("Request Failed due to "+str(e))
        
    
    def send_onchain_btc(self, payment_request: BtcOnChainPayment) -> dict:
        """sends onchain btc payment to Bitnob

        Args:
            payment_request (BtcOnChainPayment): payment request to be sent to Bitnob
            Sample data:
                'satoshis': 100000000,
                'address': '1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX',
                'customerEmail': 'mail@mail.com',
                'description': 'test',
                'priorityLevel': 'regular'

        Returns:
            dict: response from Bitnob
            sample_data: {
                "id": "1e258349-2043-4ca1-b39c-8418f9e0d36d",
                "status": "pending",
                "address": "1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX",
                "satoshis": 100000000,
                "customerEmail": "mail@mail.com",
                "description": "test",
                "priorityLevel": "regular",
            }

        Raises:
            Exception: if payment request fails
            Exception: if connection fails
        """
        url = f"{self.base_url}{self.__onchain_btc_endpoint}"

        data = payment_request.to_reqeust_payload()

        try:
            if self.verify_address(data["address"]):
                response = requests.post(url, json=data, headers=self.headers)

                if response.status_code == 200:
                    response_data = response.json()["data"]

                    payment_request.set_id(response_data["id"])
                    payment_request.set_status(response_data["status"])

                    return payment_request.to_response_payload()

                raise Exception(f"Payment Failed: {response.json()['message']}")
        except (HTTPError, ConnectionError) as e:
            raise Exception(f"Request Failed due to {e}")
        
    
    def get_transaction_data(self, transaction_id: str) -> dict:
        """gets transaction status from Bitnob

        Args:
            transaction_id (str): transaction id to be checked

        Returns (dict): response from Bitnob
            Sample data: {
                "id": "1e258349-2043-4ca1-b39c-8418f9e0d36d",
                "status": "pending",
                "address": "1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX",
                "btc": 0.00011,
                "customer_email": "mail@mail.com
            }

        Raises:
            Exception: if request fails
            Exception: if trasnation is not found
        """

        url = f"{self.base_url}{self.__transactions_endpoint}/{transaction_id}"

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                response_data = response.json()["data"]

                return {
                    "id": response_data["id"],
                    "status": response_data["status"],
                    "address": response_data["address"],
                    "btc": response_data["btcAmount"],
                    "customer_email": response_data["customer"]["email"],
                }
            raise Exception(f"{response.json()['message']}")
        except (HTTPError, ConnectionError) as e:
            raise Exception(f"Error getting transaction data: {e}")