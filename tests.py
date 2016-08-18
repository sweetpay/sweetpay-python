# -*- coding: utf-8 -*-
import pytest
from sweetpay import subscription, checkout


@pytest.fixture(
    params=[
        checkout.SubscriptionSchema, checkout.CallbackEnvelope,
        checkout.CallbackPayloadSchema,checkout. CreateSessionRequestSchema,
        checkout.AddressSchema, checkout.CustomerSchema, checkout.EnvelopeSchema,
        checkout.NameSchema, checkout.PayloadSchema, checkout.TransactionSchema,
        checkout.VerifyPurchaseBodySchema, checkout.VerifyPurchaseReplySchema
    ]
)
def checkout_schema(request):
    return request.param


@pytest.fixture(
    params=[
        subscription.NameSchema, subscription.AddressSchema,
        subscription.CustomerSchema, subscription.SubscriptionSchema,
        subscription.EnvelopeSchema, subscription.SearchEnvelopeSchema,
        subscription.CallbackEnvelope, subscription.CreateSubscriptionSchema,
        subscription.UpdateSubscriptionSchema,
        subscription.SearchSubscriptionSchema
    ]
)
def subscription_schema(request):
    return request.param


def test_subscription_schema(subscription_schema):
    inst = subscription_schema()
    for key, field in inst.fields.items():
        pass
    raise NotImplementedError
