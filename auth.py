import os

keys = {
    'dev': {
        'public_key': os.environ.get('PAYSTACK_PUBLIC_KEY'),
        'secret_key': os.environ.get('PAYSTACK_SECRET_KEY')
    },
    'production': {
        'public_key': os.environ.get('PROD_PAYSTACK_PUBLIC_KEY'),
        'secret_key': os.environ.get('PROD_PAYSTACK_SECRET_KEY')
    }
}


def authenticate(context, environment='dev'):
    authorization = context.headers.get('Authorization')
    auth_code = authorization.split("Bearer ")[1]
    return keys[environment]['public_key'] == auth_code
