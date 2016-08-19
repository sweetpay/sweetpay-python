import logging

# Importing * is usually a death sin, but we justify it here by
# defining an __all__ in the relevant modules.
from .checkout import *
from .subscription import *
from .creditcheck import *
from .utils import configure

logger = logging.Logger("sweetpay-sdk")
