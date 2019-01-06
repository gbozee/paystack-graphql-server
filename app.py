from flask import Flask
from flask_graphql import GraphQLView
import graphene
import collections
from graphene.types.generic import GenericScalar
from graphene_utils import utils
from api import PayStack
import auth
from flask_cors import CORS

application = Flask(__name__)
CORS(application)

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


class PaystackManager(graphene.ObjectType):
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
        paystack_api = PayStack()
        result = paystack_api.get_transfer(kwargs['transfer_code'])
        return result

    def resolve_get_banks(self, info, **kwargs):
        paystack_api = PayStack()
        return paystack_api.get_banks()

    def resolve_create_transfer(self, info, **kwargs):
        paystack_api = PayStack()
        PaymentInfo = collections.namedtuple('PaymentInfo', ['recipient_code'])
        result = paystack_api.create_transfer_code(
            PaymentInfo(kwargs['recipient_code']),
            kwargs['amount'],
            reason=kwargs.get('reason', ""))
        return result

    def resolve_create_recipient(self, info, **kwargs):
        paystack_api = PayStack()
        PaymentInfo = collections.namedtuple(
            'PaymentInfo', ['account_name', 'account_id', 'bank'])
        instance = PaymentInfo(**kwargs)

        result = paystack_api.create_recipient(instance)
        return result

    def resolve_account_balance(self, info, **kwargs):
        paystack_api = PayStack()
        result = paystack_api.check_balance()
        if kwargs.get('currency'):
            return [
                r for r in result
                if r['currency'].lower() == kwargs['currency'].lower()
            ]
        return result


class Query(graphene.ObjectType):
    paystack_endpoint = graphene.Field(PaystackManager)

    def resolve_paystack_endpoint(self, info, **kwargs):
        is_authorized = auth.authenticate(info.context)
        if is_authorized:
            return PaystackManager()


schema = graphene.Schema(query=Query, auto_camelcase=False)

application.add_url_rule(
    '/',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))
