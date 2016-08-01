if __name__ == "__main__":
    from sweetpay.checkout import CheckoutClient
    client = CheckoutClient(auth_token="NNq7Rcnb8y8jGTsU", stage=True,
                            version=1)
    resp = client.create_session(
        transactions=[{"amount": 100, "currency": "SEK"}],
        merchant_id="paylevo-check", country="SE"
    )
