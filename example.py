# -*- coding: utf-8 -*-

if __name__ == "__main__":
    import sweetpay
    from sweetpay import Subscription, CheckoutSession, Creditcheck
    from datetime import date, datetime

    version = {"subscription": 1, "creditcheck": 2}
    sweetpay.configure(
        "paylevo", True, version=version)
