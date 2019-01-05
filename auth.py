import os


def authenticate(context):
    authorization = context.headers.get('Authorization')
    auth_code = authorization.split("Bearer ")[1]
    return os.environ['PAYSTACK_PUBLIC_KEY'] == auth_code
