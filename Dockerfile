# FROM revolutionsystems/python:3.6.3-wee-optimized-lto as python-base
FROM python:3.6-alpine3.6
ENV PYTHONUNBUFFERED 1
# RUN apt-get update && apt-get install -y git build-essential

RUN apk add --update git
COPY requirements /requirements

RUN pip install -r /requirements/base.txt
COPY . /application

RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

ARG secret_key
ARG public_key
ARG prod_public_key
ARG prod_secret_key

ENV PAYSTACK_SECRET_KEY=$secret_key
ENV PAYSTACK_PUBLIC_KEY=$public_key
ENV PROD_PAYSTACK_SECRET_KEY=$prod_secret_key
ENV PROD_PAYSTACK_PUBLIC_KEY=$prod_public_key
EXPOSE 5000

WORKDIR /application

CMD waitress-serve --port=5000 app:application
