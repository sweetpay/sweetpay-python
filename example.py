# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from sweetpay import SweetpayClient
    from datetime import date, datetime

    version = {"subscription": 1, "creditcheck": 2, "checkout_session": 1}
    client = SweetpayClient("paylevo", True, version=version, timeout=5)
