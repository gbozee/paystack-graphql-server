from paystack.utils import PaystackAPI
import logging
import requests
from auth import keys
logger = logging.getLogger(__name__)

PAYSTACK_BASE_URL = 'https://api.paystack.co'


class PayStack(object):
    def __init__(self, environment='dev'):
        self.api = PaystackAPI(
            django=False,
            base_url=PAYSTACK_BASE_URL,
            public_key=keys[environment]['public_key'],
            secret_key=keys[environment]['secret_key'])

        self.headers = {
            "Authorization": "Bearer %s" % keys[environment]['secret_key'],
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
        result = self.api.transaction_api.initialize_transaction(
            reference=data['reference'],
            email=data['email'],
            amount=data['amount'],
            callback_url=data['callback_url'])
        if result[0]:
            return result[2]

    def recurrent_charge(self, data):
        result = self.api.transaction_api.recurrent_charge(
            authorization_code=data['authorization_code'],
            email=data['email'],
            amount=data['amount'])
        if result[0]:
            return result[2]

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
        result = self.api.transfer_api.get_banks()
        if result[0]:
            return result[2]

    def get_bank_code(self, bank_name):
        return self.api.transfer_api.get_bank_code(bank_name)

    def can_charge_client(self, data):
        result = self.api.transaction_api.check_authorization(
            authorization_code=data['authorization_code'],
            email=data['email'],
            amount=data['amount'])
        return result[2]

    def all_transactions(self, filters):
        result = self.api.transaction_api.get_transactions(
            perPage=filters.get('perPage', 50),
            customer_id=filters.get('customer_id'),
            status=filters.get('status'),
            _from=filters.get('_from'),
            _to=filters.get('_to'),
            amount=filters.get('amount'))
        if result[0]:
            return result[2]
