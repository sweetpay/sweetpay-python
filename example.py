"""
Copyright (C) 2015 David Buresund - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by David Buresund <david.buresund@gmail.com>, September 2015
"""

if __name__ == "__main__":
    import sweetpay
    from sweetpay import Subscription, CheckoutSession, Creditcheck
    from datetime import date, datetime
    sweetpay.configure("paylevo", True)
