from enum import Enum


class PaymentPriority(str, Enum):
    """Enum choices for payment priority"""

    REGULAR = "regular"
    HIGH = "high"


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
    """Schema for onchain btc payment
    """

    def __init__(
        self,
        btc_amount: float,
        address: str,
        customerEmail: str,
        description: str,
        priorityLevel: PaymentPriority = PaymentPriority.REGULAR,
    ):  
        self.__btc_amount = btc_amount
        self.__address = address
        self.__customerEmail = customerEmail
        self.__description = description
        self.__priorityLevel = priorityLevel

    def to_reqeust_payload(self) -> dict:
        """Return dict representation of onchain btc payment
        """
        return {
            "satoshis": self.__btc_amount * 100000000,
            "address": self.__address,
            "customerEmail": self.__customerEmail,
            "description": self.__description,
            "priorityLevel": self.__priorityLevel,
        }

class BtcLightningPayment:
    """Schema for lightning btc payment
    """

    def __init__(
        self,
        btc_amount: float, 
        lnAddress: str,
        reference: str,
        customer_email: str,
    ):
        
        self.__btc_amount = btc_amount
        self.__lnAddress = lnAddress
        self.__reference = reference
        self.__customer_email = customer_email
        
    def to_request_payload(self) -> dict:
        """ Return dict representation of lightning btc payment
        """
        return {
            "satoshis": self.__btc_amount * 100000000,
            "lnAddress": self.__lnAddress,
            "reference": self.__reference,
            "customerEmail": self.__customer_email,
        }
    
       