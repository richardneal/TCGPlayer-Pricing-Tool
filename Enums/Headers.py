# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from enum import Enum


# Make sure to preserve this order, which matches the TCGPlayer-generated CSV
class Headers(Enum):
    TCGPLAYER_ID = 'TCGplayer Id'
    PRODUCT_LINE = 'Product Line'
    SET_NAME = 'Set Name'
    PRODUCT_NAME = 'Product Name'
    TITLE = 'Title'
    NUMBER = 'Number'
    RARITY = 'Rarity'
    CONDITION = 'Condition'
    MARKET_PRICE = 'TCG Market Price'
    DIRECT_LOW_PRICE = 'TCG Direct Low'
    LOW_PRICE_WITH_SHIPPING = 'TCG Low Price With Shipping'
    LOW_PRICE = 'TCG Low Price'
    TOTAL_QUANTITY = 'Total Quantity'
    ADD_TO_QUANTITY = 'Add to Quantity'
    MARKETPLACE_PRICE = 'TCG Marketplace Price'
    PHOTO_URL = 'Photo URL'
