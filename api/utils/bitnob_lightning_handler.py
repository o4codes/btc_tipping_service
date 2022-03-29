from requests import HTTPError
import requests
from decouple import config
from api.utils.schemas import BtcLightningPayment
from api.utils.bitnob_base import BitnobBase


class BtcLighteningHandler(BitnobBase):
    """class handles all requests to the BTC lighterning API
    """

    def __init__(self) -> None:
        super().__init__()
        self.__validate_ln_address = "/api/v1/lnurl/decodelnaddress"
        self.__pay_ln_address = "/api/v1/lnurl/paylnaddress"
        self.__transactions_endpoint = "/api/v1/transactions"

    
    def verify_lightning_address(self, lnAddress: str) -> bool:
        """ Verifies a lightning address to for validity
        
        Args:
            address (str): address to be verified

        Returns:
            Dict: response from Btinob with details about the address
            Sample {
                    "image": "",
                    "identifier": "fiatjaf@dollar.lol",
                    "description": "Satoshis to fiatjaf@dollar.lol.",
                    "callback": "https://dollar.lol/.well-known/lnurlp/fiatjaf",
                    "commentAllowed": 0,
                    "satMinSendable": 1,
                    "satMaxSendable": 100000
                    }
        Raises:
            Exception: if request fails
        """
        
        url = f"{self.base_url}{self.__validate_ln_address}"
        data = {"lnAddress": lnAddress}
        try:
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code == 200:
                return response.json()['data']
            raise Exception("LnAddress not valid")
        except (HTTPError, ConnectionError) as e:
            raise Exception("Request Failed due to " + str(e))
        
    
    def pay_lightning_address(self, lightning_payment: BtcLightningPayment) -> dict:
        """sends payment to lightning address
        
        Args:
            lightning_payment (BtcLightningPayment): payment details
        
        Returns:
            Dict: response from Btinob with details about the address
            
        Raises:
            Exception: if request fails
        """
        
        url = f"{self.base_url}{self.__pay_ln_address}"
        data = lightning_payment.to_request_payload()
        try:
            verify_data = self.verify_lightning_address(data["lnAddress"])
            if data['satoshis'] > verify_data['satMaxSendable']:
                raise Exception("Amount is larger than maximum sendable")
            
            if data['satoshis'] < verify_data['satMinSendable']:
                raise Exception("Amount is smaller than minimum sendable")
            
            response = requests.post(url, json=data, headers=self.headers)
            data = response.json()
            if response.status_code == 200:
                if data['data']['status'] == "ERROR":
                    raise Exception(data['data']['message'])
                
                lightning_payment.set_id(data['data']['id'])
                return lightning_payment.to_response_payload()
            
            raise Exception(f"{data['message']}")
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
            raise Exception(f"Request Failed due to {e}")