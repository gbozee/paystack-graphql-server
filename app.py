from flask import Flask
from flask_graphql import GraphQLView
import graphene
import auth
from flask_cors import CORS
import l_types

application = Flask(__name__)
CORS(application)


class PaystackManager(l_types.TransferType):
    pass


def authenticate(info, kwargs, klass):
    is_authorized = auth.authenticate(
        info.context, environment=kwargs['environment'])
    if is_authorized:
        return klass(environment=kwargs['environment'])


class Query(graphene.ObjectType):
    paystack_endpoint = graphene.Field(
        PaystackManager, environment=graphene.String(required=True))
    transfers = graphene.Field(
        l_types.TransferType, environment=graphene.String(required=True))

    customers = graphene.Field(
        l_types.CustomerType, environment=graphene.String(required=True))
    transactions = graphene.Field(
        l_types.TransactionType, environment=graphene.String(required=True))

    def resolve_paystack_endpoint(self, info, **kwargs):
        return authenticate(info, kwargs, PaystackManager)

    def resolve_transfers(self, info, **kwargs):
        return authenticate(info, kwargs, l_types.TransferType)

    def resolve_transactions(self, info, **kwargs):
        return authenticate(info, kwargs, l_types.TransactionType)

    def resolve_customers(self, info, **kwargs):
        return authenticate(info, kwargs, l_types.CustomerType)


schema = graphene.Schema(query=Query, auto_camelcase=False)

application.add_url_rule(
    '/',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))
