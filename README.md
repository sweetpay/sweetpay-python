# Sweetpay SDK

This is a Python SDK for SweetPay's different APIs. Note that this library is not production ready yet. The checkout (v1), creditcheck (v2) and subscription (v1) API is currently only supported.

The documentation of the underlying APIs can be found [here](https://developers.sweetpayments.com/docs/).

Some tests have been written for the subscription API, which makes it the currently most stable part of the SDK. 

## API documentations
1. [Subscription API](#subscription-api)

## Installation
You can use `pip` to install the SDK.
```
pip install sweetpay
```

## Configuring the SDK
```python
from sweetpay import configure
configure("<your-api-token>", stage=True, version={"subscription": 1})
```

Note that all code examples below this point will assume that you've already configured the SDK as shown above.

## General use

```python
from sweetpay import Subscription

# Use an operation
resp = Subscription.search(merchantId="<your-merchant-id>")

# For getting the data returned from the server. Will be 
# `None` if JSON wasn't provided. 
resp.data

# For fetching the HTTP status code.
resp.code

# For getting the status passed from the server. For 
# example "OK" or "MISSING_COUNTRY".
resp.status

# For fetching the underlying `requests` response. If you don't 
# know what to use this for, the odds are that you don't have a 
# need for it.
resp.response
```

## Validation and deserialization
In order to deserialize the response from the server, the SDK exposes a `validates` decorator, which can be used to turn. The SDK already has a couple of validators configured, mainly to convert strings to datetime and date objects.
 
```python
from sweetpay import Subscription
from sweetpay.utils import decode_datetime

# Note how we specify the path to the attribute. If the 
# path to the attribute simply can't be found, the 
# validator will be ignored.
@Subscription.validates("payload", "startsAt")
def validate_starts_at(value):
    return decode_datetime(value)
    
# This can also be useful when you want to transform a 
# value from Sweetpay to, for example, your own `enum.Enum` object.
# However, this should be used with care, as you cannot guarantee
# that Sweetpay doesn't add values, which you haven't stored in  
# your enum.
@Subscription.validates("payload", "interval")
def validate_interval(value):
    return MyIntervalEnum(value)

# Use `sweetpay.BaseResource.validates` if you want to set a 
# validator for all APIs.
```

For more advanced validation and deserialization, you can use something like [marshmallow](https://marshmallow.readthedocs.io/en/latest/) with the data returned from the SDK. 

## Dynamic configuration
Sometimes you want to be able to set the configuration dynamically. For example configuring different timeouts for different operations. You can currently only configure the `timeout` on an operation basis, but support for more parameters can be built in if requested.

```python
from sweetpay import Subscription

Subscription.search(country="SE", timeout=10)
```

## Error handling

If you're calling an operation on a resource (e.g. `Subscription.create`) and no exception is raised, you can rest assured that the operation succeeded. If something goes wrong, an exception will be raised.

All exceptions exposes the `data`, `response`, `status`, `code` and `exc` attribute. None of them are guaranteed to have a value other than `None`, but they can be useful when you want to know the source of the error.

```python
from sweetpay import Subscription
from sweetpay.errors import *

try:
    # Use an operation
    resp = Subscription.regret(subscription_id)

except FailureStatusError as e:
    # Whenever you get this, you would do best to inspect the 
    # status, to figure out what went wrong. 
    if e.status == "NOT_MODIFIABLE":
        print("Oh, the subscription can't be modified")
    else:
        print("Oh, something else happened")
        
except UnauthorizedError as e:
    # You are simply unauthorized. Check your API token, 
    # or contact Sweetpay's developer to configure it correctly.
    print("Wrong API token!")
    
except NotFoundError as e:
    # The resource ID (e.g. `subscription_id`) did not match 
    # an existing resource. Do some soul searching or why not 
    # try to search (e.g. `Subscription.search`) for the 
    # subscription you're looking for?
    print("The resource couldn't be found on the server")

except ProxyError as e:
    # A proxy error occurred. It's usually best to just
    # retry in this case.
    print("Maybe retry?")

except MethodNotAllowedError as e:
    # If you receive this status, there is something wrong with  
    # the SDK, as no invalid HTTP methods should used when  
    # communicating with the server. Contact Sweetpay's developers.
    print("Wrong HTTP method sent to the API endpoint!")

except UnderMaintenanceError as e:
    # Just try again later.
    print("The API is under maintenance.")

except (BadDataError, InvalidParameterError) as e:
    # Inspect `e.data`, `e.status` or both. `e.data` is 
    # sometimes `None` in this case, so be wary.
    print("You passed bad data to the server")

except InternalServerError as e:
    # Contact Sweetpay's developers if this happens. It 
    # shouldn't happen.
    print("Something went wrong on Sweetpay's server.")

except TimeoutError as e:
    # Try again, and maybe set a higher timeout.
    print("A timeout occurred!")

except RequestError as e:
    # The parent of all errors stemming from the underlying 
    # `requests` library. If you want to know the details, 
    # try inspecting the `e.exc` for gaining access to the 
    # real exception.
    print("The real exception:", e.exc)

except SweetpayError as e:
    # The parent of all errors. 
    print("You can catch all errors with this one")
```

## Subscription API

This part explains how to interact with the subscription API.

### Create a subscriptions

[Follow this link for the API documentation and the available parameters](https://developers.sweetpayments.com/docs/subscription/apiref/#create-a-subscription)

```python
from sweetpay import Subscription
from datetime import datetime
from decimal import Decimal

resp = Subscription.create(
    amount=Decimal("200.0"), currency="SEK", 
    country="SE", merchantId="<your-merchant-id>",
    interval="MONTHLY", ssn="19500101-0001",
    startsAt=datetime.utcnow().date())
```

### Update a subscription
[Follow this link for the API documentation and the available parameters](https://developers.sweetpayments.com/docs/subscription/apiref/#update-a-subscription)

```python
from sweetpay import Subscription

resp = Subscription.update(subscription_id, maxExecutions=4)
```

### Regret a subscription
[Follow this link for the API documentation and the available parameters](https://developers.sweetpayments.com/docs/subscription/apiref/#regret-a-subscription)
```python
from sweetpay import Subscription

resp = Subscription.regret(subscription_id)
```

### Query a subscription
[Follow this link for the API documentation and the available parameters](https://developers.sweetpayments.com/docs/subscription/apiref/#query-a-subscription)
```python
from sweetpay import Subscription

resp = Subscription.query(subscription_id)
```

### Search for subscriptions
[Follow this link for the API documentation and the available parameters](https://developers.sweetpayments.com/docs/subscription/apiref/#search-for-subscriptions)
```python
from sweetpay import Subscription

resp = Subscription.search(country="SE")
```

### Listing the log for a subscription
```python
from sweetpay import Subscription

resp = Subscription.list_log(subscription_id)
```
