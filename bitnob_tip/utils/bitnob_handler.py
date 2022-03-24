from urllib.error import HTTPError
import requests
from decouple import config

from .schemas import (
    PaymentPriority,
    BitnobCustomer,
    BtcOnChainPayment,
    BtcLightningPayment,
)


class BitnobHandler:
    """class handles all requests to the Bitnob API"""

    def __init__(self) -> None:
        self.__base_url = "https://sandboxapi.bitnob.co"
        self.__customer_endpoint = "/api/v1/customers"
        self.__onchain_btc_endpoint = "/api/v1/wallets/send_bitcoin"
        self.__lightining_endpoint = "/api/v1/lnurl/paylnaddress"
        self.__lightining_address = "/api/v1/lnurl/decodelnaddress"
        self.__transactions_endpoint = "/api/v1/transactions"
        self.__secret_key = config("BITNOB_SECRET_KEY")
        self.__public_key = config("BITNOB_PUBLIC_KEY")

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

        url = f"{self.__base_url}{self.__customer_endpoint}"

        headers = {
            "Authorization": f"Bearer {self.__secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        data = customer.to_request_payload()

        try:
            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                return response.json()["data"]

            raise Exception(f"Creation Error: {response.json()['message']}")

        except (HTTPError, ConnectionError) as e:
            raise Exception(f"Error creating customer: {e}")

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
        url = f"{self.__base_url}{self.__onchain_btc_endpoint}"

        headers = {
            "Authorization": f"Bearer {self.__secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        data = payment_request.to_reqeust_payload()

        try:
            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                response_data = response.json()["data"]

                payment_request.set_id(response_data["id"])
                payment_request.set_status(response_data["status"])

                return payment_request.to_response_payload()

            raise Exception(f"Payment Failed: {response.json()['message']}")
        except (HTTPError, ConnectionError) as e:
            raise Exception(f"Error sending onchain btc: {e}")

    def decode_lightning_address(self, ln_address: str):
        """Decodes a lightning address

        Args:
            ln_address (str): lightning address to be decoded

        Returns:
            dict: response from Bitnob to represnet range
            sample data: {
                "satMinSendable": 1,
                "satMaxSendable": 100000
            }

        Raises:
            Exception: if request fails
            Exception: if connection fails
        """
        url = f"{self.__base_url}{self.__lightining_address}"

        headers = {
            "Authorization": f"Bearer {self.__secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        data = {"lnAddress": ln_address}

        try:
            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                response_data = response.json()["data"]
                return response_data

            raise Exception(f"Payment Failed: {response.json()['message']}")
        except (HTTPError, ConnectionError) as e:
            raise Exception(f"Error decoding lightning address: {e}")

    def send_lightning_payment(self, payment_request: BtcLightningPayment) -> dict:
        """sends lightning payment to Bitnob

        Args:
            payment_request (PaymentPriority): payment request to be sent to Bitnob
            Sample data:
                'btc_amount': 100000000,
                'customerEmail': 'mail@mail.com
                'lnAddress:'sdsdsds',
                'reference':'asasas'

        Returns:
            dict: response from Bitnob

        Raises:
            Exception: if payment request fails
            Exception: if connection fails
            Exception: if amount is not within range
        """
        url = f"{self.__base_url}{self.__lightining_endpoint}"

        headers = {
            "Authorization": f"Bearer {self.__secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        data = payment_request.to_request_payload()

        amount_range = self.decode_lightning_address(data["lnAddress"])
        min_btc = int(amount_range["satMinSendable"])/100000000
        max_btc = int(amount_range["satMaxSendable"])/100000000
        
        if (data["satoshis"] >= amount_range["satMinSendable"]) and (
            data["satoshis"] <= amount_range["satMaxSendable"]
        ):
            try:
                response = requests.post(url, json=data, headers=headers)

                if response.status_code == 200:
                    return response.json()["data"]

                raise Exception(f"Payment Failed: {response.json()['message']}")
            except (HTTPError, ConnectionError) as e:
                raise Exception(f"Error sending lightning payment: {e}")
        raise Exception(f"""
                        BTC Amount to send is not within sendable range\n
                        Min BTC: {min_btc}, Max BTC: {max_btc}
                        """ )

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
            raise Exception(f"Error sending lightning payment: {e}")
