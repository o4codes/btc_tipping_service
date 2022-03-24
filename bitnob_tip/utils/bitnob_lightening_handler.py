from urllib.error import HTTPError
import requests
from decouple import config
from .schemas import BtcLightningPayment


class BtcLighteningHandler:
    """class handles all requests to the BTC lighterning API
    """

    def __init__(self) -> None:
        self.__base_url = "https://sandboxapi.bitnob.co"
        self.__lightining_endpoint = "/api/v1/lnurl/paylnaddress"
        self.__lightining_address = "/api/v1/lnurl/decodelnaddress"
        self.__secret_key = config("SECRET_KEY")
        self.__headers = {
            "Authorization": f"Bearer {self.__secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }


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

        data = {"lnAddress": ln_address}

        try:
            response = requests.post(url, json=data, headers=self.__headers)

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
                print(response)

                if response.status_code == 200:
                    return response.json()["data"]

                raise Exception(f"Payment Failed: {response.json()['message']}")
            except (HTTPError, ConnectionError) as e:
                raise Exception(f"Error sending lightning payment: {e}")
        raise Exception(f"""
                        BTC Amount to send is not within sendable range\n
                        Min BTC: {min_btc}, Max BTC: {max_btc}
                        """ )

