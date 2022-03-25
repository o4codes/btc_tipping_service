from enum import Enum
from uuid import uuid4

class PaymentPriority(str, Enum):
    """Enum choices for payment priority"""

    REGULAR = "regular"
    HIGH = "high"


class PaymentStatus(str, Enum):
    """Enum choices for payment status"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class BitnobCustomer:
    """Schema for customer data"""

    def __init__(
        self, firstName: str, lastName: str, email: str, phone: str, countryCode: str
    ):
        self.__firstName = firstName
        self.__lastName = lastName
        self.__email = email
        self.__phone = phone
        self.__countryCode = countryCode

    def to_request_payload(self) -> dict:
        """Return dict representation of customer data"""
        return {
            "firstName": self.__firstName,
            "lastName": self.__lastName,
            "email": self.__email,
            "phone": self.__phone,
            "countryCode": self.__countryCode,
        }


class BtcOnChainPayment:
    """Schema for onchain btc payment"""

    def __init__(
        self,
        btc_amount: float,
        address: str,
        customer_email: str,
        description: str,
        priorityLevel: PaymentPriority = PaymentPriority.REGULAR,
    ):
        self.__address = address
        self.__customerEmail = customer_email
        self.__description = description
        self.__priorityLevel = priorityLevel.value
        self.__satoshis = btc_amount * 100000000
        self.__status = None
        self.__id = None

    def set_id(self, id: str) -> None:
        """Set id for onchain btc payment"""
        self.__id = id

    def set_status(self, status: PaymentStatus) -> None:
        """Set status for onchain btc payment"""
        self.__status = status

    def to_reqeust_payload(self) -> dict:
        """Return dict representation of onchain btc payment"""
        return {
            "satoshis": self.__satoshis,
            "address": self.__address,
            "customerEmail": self.__customerEmail,
            "description": self.__description,
            "priorityLevel": self.__priorityLevel,
        }

    def to_response_payload(self) -> None:
        """Return a response dict structure for onchain btc payment"""
        return {
            "id": self.__id,
            "status": self.__status,
            "satoshis": self.__satoshis,
            "address": self.__address,
            "customerEmail": self.__customerEmail,
            "description": self.__description,
            "priorityLevel": self.__priorityLevel,
        }


class BtcLightningPayment:
    """Schema for lightning btc payment"""

    def __init__(
        self,
        btc_amount: float,
        description: str,
        sender_email: str,
        receiver_email: str,
    ):

        self.__description = description
        self.__sender_email = sender_email
        self.__receiver_email = receiver_email
        self.__satoshis = btc_amount * 100000000
        self.__reference = uuid4()
        self.__request = None
        self.__id = None
        
    def set_request(self, request: str) -> None:
        """Set reference for lightning btc payment
        """
        self.__request = request
    
    def set_id(self, id: str) -> None:
        """Set id for lightning btc payment"""
        self.__id = id


    def to_create_invoice_request_payload(self) -> dict:
        """Return dict representation of lightning btc payment"""
        return {
            "satoshis": self.__satoshis,
            "description": self.__description,
            "customerEmail": self.__receiver_email,
        }
    
    def to_initiate_paymnet_request_payload(self) -> dict:
        """Return dict representation of lightning btc payment"""
        return {
            "request": self.__request
        }
        
    def to_invoice_request_payment(self) -> dict:
        """Return dict representation of lightning btc payment"""
        return {
            "request": self.__request,
            "reference": self.__reference,
            "customerEmail": self.__sender_email,
        }
        
    def to_response_payload(self) -> dict:
        """ Response of all requests
        """
        return {
            "id": self.__id,
            "reference": self.__reference,
            "request": self.__request,
            "btcAmount": self.__satoshis / 100000000,
            'satoshis': self.__satoshis,
            "senderEmail": self.__sender_email,
            "receiverEmail": self.__receiver_email,
            "status": "pending",
        }


class ResponseData:
    @staticmethod
    def success(data: dict) -> dict:
        """Return a success response"""
        return {"status": True, "data": data}

    @staticmethod
    def error(message: str) -> dict:
        """Return an error response"""
        return {"status": False, "message": message}
