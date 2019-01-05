from paystack.utils import PaystackAPI
import logging
import requests
import os
logger = logging.getLogger(__name__)

PAYSTACK_BASE_URL = 'https://api.paystack.co'

PAYSTACK_SECRET_KEY = os.environ['PAYSTACK_SECRET_KEY']


class PayStack(object):
    def __init__(self):
        self.api = PaystackAPI(
            django=False,
            base_url=PAYSTACK_BASE_URL,
            public_key=os.environ['PAYSTACK_PUBLIC_KEY'],
            secret_key=PAYSTACK_SECRET_KEY)

    headers = headers = {
        "Authorization": "Bearer %s" % PAYSTACK_SECRET_KEY,
        "Content-Type": "application/json",
    }

    def create_customer(self, data):
        r = requests.post(
            PAYSTACK_BASE_URL + "/customer", json=data, headers=self.headers)
        if r.status_code >= 400:
            raise (requests.HTTPError)
        return r.json()["data"]["customer_code"]

    def validate_transaction(self, ref):
        result = self.api.transaction_api.verify_payment(ref)
        data = result[2]
        if result[0]:
            return dict(
                authorization_code=data["authorization"]["authorization_code"],
                amount_paid=data["amount"] / 100,
            )
        return None

    def initialize_transaction(self, data):
        """
        Initializing transaction from server us
        :data : {
            'reference','email','amount in kobo',
            'callback_url'
        }
        """
        r = requests.post(
            PAYSTACK_BASE_URL + "/transaction/initialize",
            json=data,
            headers=self.headers,
        )
        if r.status_code >= 400:
            logger.info(r.text)
            r.raise_for_status()
        if r.json()["status"]:
            return r.json()["data"]
        return {}

    def recurrent_charge(self, data):
        """
        When attempting to bill an existing customers that has already paid through us
        :data : {
            'authorization_code','email','amount'
        }
        """
        r = requests.post(
            PAYSTACK_BASE_URL + "/transaction/charge_authorization",
            json=data,
            headers=self.headers,
        )
        if r.status_code >= 400:
            r.raise_for_status()
        logger.info(r.json())
        if r.json()["status"]:
            return True
        return False

    def create_recipient(self, payout_details):
        """bank, account_id,account_name"""
        result = self.api.transfer_api.create_recipient(
            account_name=payout_details.account_name,
            account_id=payout_details.account_id,
            bank=payout_details.bank)
        if result[0]:
            return result[2]

    def initialize_transfer(self, amount, recipient, reason):
        result = self.api.transfer_api.initialize_transfer(
            amount, recipient, reason)
        return result

    def create_transfer_code(self, payout, amount, reason=""):
        data = self.initialize_transfer(amount, payout.recipient_code, reason)
        return self._transfer_response(data)

    def _transfer_response(self, result):
        if len(result) == 3:
            transfer_code = result[2]['transfer_code']
            msg = result[1]
            return transfer_code, msg
        return None, None

    def verify_transfer(self, transfer_recipient, code):
        """verify transaction"""
        result = self.api.transfer_api.verify_transfer(transfer_recipient,
                                                       code)
        if result[0]:
            return result[1].get('data')

    def enable_otp(self, status=True, code=None):
        return self.api.transfer_api.enable_otp(status, code=None)

    def resend_otp(self, transfer_recipient):
        return self.api.transfer_api.resend_otp(transfer_recipient)

    def get_transfer(self, transfer_recipient):
        """Fetch the transfer for a given recipient"""
        result = self.api.transfer_api.get_transfer(transfer_recipient)
        if result[0]:
            return result[2]

    def check_balance(self):
        return self.api.transfer_api.check_balance()

    def get_banks(self):
        req = requests.get(
            PAYSTACK_BASE_URL + "/bank",
            headers=self.headers,
        )
        if req.status_code >= 400:
            req.raise_for_status()
        return req.json()['data']

    def get_bank_code(self, bank_name):
        options = {
            "Citibank": "023",
            "Access Bank": "044",
            "Diamond Bank": "063",
            "Ecobank Nigeria": "050",
            "Enterprise Bank": "084",
            "Fidelity Bank Nigeria": "070",
            "First Bank of Nigeria": "011",
            "First City Monument Bank": "214",
            "Guaranty Trust Bank": "058",
            "Heritage Bank": "030",
            "Keystone Bank Limited": "082",
            "Mainstreet Bank": "014",
            "Skye Bank": "076",
            "Stanbic IBTC Bank": "221",
            "Standard Chartered Bank": "068",
            "Sterling Bank": "232",
            "Union Bank of Nigeria": "032",
            "United Bank for Africa": "033",
            "Unity Bank": "215",
            "Wema Bank": "035",
            "Zenith Bank": "057",
            "Jaiz Bank": "301",
            "Suntrust Bank": "100",
            "Providus Bank": "101",
            "Parallex Bank": "526",
        }
        return options.get(bank_name)
