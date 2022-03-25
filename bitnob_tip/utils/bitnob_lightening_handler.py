from requests import HTTPError
import requests
from decouple import config
from .schemas import BtcLightningPayment


class BtcLighteningHandler:
    """class handles all requests to the BTC lighterning API
    """

    def __init__(self) -> None:
        self.__base_url = "https://sandboxapi.bitnob.co"
        self.__lightining_invoice_creation = "/api/v1/wallets/ln/createinvoice"
        self.__lightning_initiate_payment = "/api/v1/wallets/ln/initiatepayment"
        self.__lightning_pay_invoice = "/api/v1/wallets/ln/pay"
        self.__transactions_endpoint = "/api/v1/transactions"
        self.__secret_key = config("BITNOB_SECRET_KEY")
        self.__headers = {
            "Authorization": f"Bearer {self.__secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }


    def create_invoice(self, payment_request: BtcLightningPayment) -> BtcLightningPayment:
        """ Receiver creates a lightning invoice

        Args:
            payment_request (BtcLightningPayment): payment request to be sent to Bitnob

        Returns:
            payment_request (BtcLightningPayment): data returned as object from Bitnob
        """
        url = f"{self.__base_url}{self.__lightining_invoice_creation}"
        data = payment_request.to_create_invoice_request_payload()
        try:
            response = requests.post(url, json=data, headers=self.__headers)
            if response.status_code == 200:
                request = response.json()["data"]["request"]
                payment_request.set_request(request)
                return payment_request
            raise Exception("Error creating invoice: " + response.text)
        except (HTTPError, ConnectionError) as e:
            raise Exception("Error creating invoice: " + str(e))
    
    
    def initiate_request(self, payment_request: BtcLightningPayment) -> bool:
        """ Used to verify payment request by sender

        Args:
            payment_request (BtcLightningPayment): payment request to be sent to Bitnob

        Returns:
            bool: True if payment is valid, False otherwise
        """
        url = f"{self.__base_url}{self.__lightning_initiate_payment}"
        data = payment_request.to_initiate_paymnet_request_payload()
        try:
            response = requests.post(url, json=data, headers=self.__headers)
            if response.status_code == 200:
                if response.json()["data"]["isExpired"] == False:
                    return True
                return False
            raise Exception("Error initiating payment: " + response.text)
        except (HTTPError, ConnectionError) as e:
            raise Exception("Error initiating payment: " + str(e))
        
        
    def pay_invoice(self, payment_request: BtcLightningPayment) -> BtcLightningPayment:
        """ Sender pays invoice

        Args:
            payment_request (BtcLightningPayment): payment request to be sent to Bitnob

        Returns:
            payment_request (BtcLightningPayment): data returned as object from Bitnob
        """
        url = f"{self.__base_url}{self.__lightning_pay_invoice}"
        data = payment_request.to_invoice_request_payment()
        try:
            response = requests.post(url, json=data, headers=self.__headers)
            if response.status_code == 200:
                payment_request.set_id(response.json()["data"]["id"])
                return payment_request
            raise Exception("Error paying invoice: " + response.text)
        except (HTTPError, ConnectionError) as e:
            raise Exception("Error paying invoice: " + str(e))
    
      
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

        url = f"{self.__base_url}{self.__transactions_endpoint}/{transaction_id}"

        headers = {
            "Authorization": f"Bearer {self.__secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.get(url, headers=headers)
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