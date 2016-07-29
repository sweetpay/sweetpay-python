"""
Copyright (C) 2015 David Buresund - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by David Buresund <david.buresund@gmail.com>, September 2015
"""

if __name__ == "__main__":
    from sweetpay.checkout import CheckoutClient
    client = CheckoutClient(auth_token="NNq7Rcnb8y8jGTsU", stage=True,
                            version=1)
    resp = client.create_session(
        transactions=[{"amount": 100, "currency": "SEK"}],
        merchant_id="paylevo-check", country="SE"
    )
