import graphene
import collections
from graphene.types.generic import GenericScalar
from graphene_utils import utils
from api import PayStack

PaystackRecipientData = utils.createGrapheneClass(
    'PaystackRecipientData', [('recipient_code', str), ('type', str),
                              ('name', str), ('details', 'json')])

PaystackAccountBalance = utils.createGrapheneClass(
    "PaystackAccountBalance", [('currency', str), ('balance', float)])
PaystackTransferData = utils.createGrapheneClass(
    "PaystackTransferData",
    [('amount', float), ('status', str),
     ('recipient_code', graphene.Field(PaystackRecipientData)),
     ('createdAt', str), ('updatedAt', str)])
PaystackBankData = utils.createGrapheneClass('PaystackBankData',
                                             [('name', str), ('slug', str),
                                              ('code', str), ('type', str)])
PaystackCustomer = utils.createGrapheneClass(
    'PaystackCustomer', [('id', int), ('first_name', str), ('last_name', str),
                         ('email', str), ('phone', str),
                         ('customer_code', str), ('risk_action', str)])
PaystackCard = utils.createGrapheneClass(
    'PaystackCard', [('authorization_code', str), ('bin', str), ('last4', str),
                     ('exp_month', str), ('exp_year', str), ('channel', str),
                     ('card_type', str), ('bank', str), ('country_code', str),
                     ('brand', str), ('reusable', bool), ('signature', str)])
PaystackTransaction = utils.createGrapheneClass(
    "PaystackTransaction",
    [('id', int), ('domain', str), ('status', str), ('amount', float),
     ('paid_at', str), ('created_at', str), ('channel', str),
     ('currency', str), ('ip_address', str),
     ('customer', graphene.Field(PaystackCustomer)),
     ('authorization', graphene.Field(PaystackCard)), ('plan', 'json'),
     ('subaccount', 'json')])


class BaseKlass(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paystack_api = PayStack(self.environment)

    environment = graphene.String()


class TransferType(BaseKlass, graphene.ObjectType):
    create_recipient = graphene.Field(
        PaystackRecipientData,
        account_name=graphene.String(required=True),
        account_id=graphene.String(required=True),
        bank=graphene.String(required=True))
    get_banks = graphene.List(PaystackBankData)
    account_balance = graphene.List(
        PaystackAccountBalance, currency=graphene.String(required=False))
    create_transfer = graphene.Field(
        GenericScalar,
        recipient_code=graphene.String(required=True),
        amount=graphene.Float(required=True),
        reason=graphene.String(required=False))
    get_transfer = graphene.Field(
        PaystackTransferData, transfer_code=graphene.String(required=True))

    def resolve_get_transfer(self, info, **kwargs):
        result = self.paystack_api.get_transfer(kwargs['transfer_code'])
        return result

    def resolve_get_banks(self, info, **kwargs):
        return self.paystack_api.get_banks()

    def resolve_create_transfer(self, info, **kwargs):
        PaymentInfo = collections.namedtuple('PaymentInfo', ['recipient_code'])
        result = self.paystack_api.create_transfer_code(
            PaymentInfo(kwargs['recipient_code']),
            kwargs['amount'],
            reason=kwargs.get('reason', ""))
        return result

    def resolve_create_recipient(self, info, **kwargs):
        PaymentInfo = collections.namedtuple(
            'PaymentInfo', ['account_name', 'account_id', 'bank'])
        instance = PaymentInfo(**kwargs)

        result = self.paystack_api.create_recipient(instance)
        return result

    def resolve_account_balance(self, info, **kwargs):
        result = self.paystack_api.check_balance()
        if kwargs.get('currency'):
            return [
                r for r in result
                if r['currency'].lower() == kwargs['currency'].lower()
            ]
        return result


class TransactionType(BaseKlass, graphene.ObjectType):
    validate_transaction = graphene.Field(
        GenericScalar, code=graphene.String(required=True))
    initialize_transaction = graphene.Field(
        GenericScalar,
        reference=graphene.String(required=True),
        email=graphene.String(required=True),
        amount=graphene.Float(required=True),
        callback_url=graphene.String(required=True))
    verify_recharge = graphene.Field(
        GenericScalar,
        authorization_code=graphene.String(required=True),
        email=graphene.String(required=True),
        amount=graphene.Float(required=True))
    all_transactions = graphene.List(
        PaystackTransaction,
        # GenericScalar,
        perPage=graphene.Int(required=False),
        customer_id=graphene.Int(required=False),
        status=graphene.String(required=False),
        _from=graphene.String(required=False),
        _to=graphene.String(required=False),
        amount=graphene.Float(required=False))
    trigger_recurrent_charge = graphene.Field(
        PaystackTransaction,
        authorization_code=graphene.String(required=True),
        email=graphene.String(required=True),
        amount=graphene.Float(required=True))

    def resolve_trigger_recurrent_charge(self, info, **kwargs):
        return self.paystack_api.recurrent_charge(kwargs)

    def resolve_initialize_transaction(self, info, **kwargs):
        return self.paystack_api.initialize_transaction(kwargs)

    def resolve_validate_transaction(self, info, **kwargs):
        return self.paystack_api.validate_transaction(kwargs['code'])

    def resolve_all_transactions(self, info, **kwargs):
        result = self.paystack_api.all_transactions(kwargs)
        return result

    def resolve_verify_recharge(self, info, **kwargs):
        result = self.paystack_api.can_charge_client(kwargs)
        return result


class CustomerType(BaseKlass, graphene.ObjectType):
    pass
