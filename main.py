import csv

from Enums.Condition import Condition, Conditions
from Enums.Headers import Headers
from Enums.Price import Price, PriceType
from Enums.Rarity import Rarity
from Product import Product


def process_csv(filename: str):
    products = []
    with open(filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            # print(Product(**{header.name.lower(): row[header.value] for header in Headers}))
            products.append(Product(**{header.name.lower(): row[header.value] for header in Headers}))
    return products
            # for header in Headers:
            #     print(header.value)
            #     product_dict[header.name.lower()] = row[header.value]
            # product = Product(**product_dict)
            # p = row[h.value for h in Headers]
            # print(zip(Headers))
            # product =
            # break
            # for header in Headers:


    #         # print(row)
    #         condition = Condition(row[Headers.CONDITION])
    #         if condition.condition is Conditions.UNOPENED:
    #             rarity = Rarity.PRODUCT
    #         else:
    #             rarity = Rarity(row[Headers.RARITY])
    #         tcgplayer_id = row[Headers.TCGPLAYER_ID]
    #         number = row[Headers.NUMBER]
    #         market_price = Price(row[Headers.MARKET_PRICE])
    #         direct_low = Price(row[Headers.DIRECT_LOW])
    #         low_with_shipping = Price(row[Headers.LOW_PRICE_WITH_SHIPPING])
    #         low = Price(row[Headers.LOW_PRICE])
    #         quantity = row[Headers.TOTAL_QUANTITY]
    #         add_to = int(row[Headers.ADD_TO_QUANTITY])
    #         if row[Headers.MARKETPLACE_PRICE] == '999.9900':
    #             my_price = Price('')
    #         else:
    #             my_price = Price(row[Headers.MARKETPLACE_PRICE])
    #         photo_url = row[Headers.PHOTO_URL]
    #         product = Product(
    #             tcgplayer_id,
    #             row['Product Line'],
    #             row['Set Name'],
    #             row['Product Name'],
    #             row['Title'],
    #             number,
    #             rarity,
    #             condition,
    #             market_price,
    #             direct_low,
    #             low_with_shipping,
    #             low,
    #             quantity,
    #             add_to,
    #             my_price,
    #             photo_url
    #         )
    #         products.append(product)
    # return products


def output_csv(filename: str, products: list[Product]):
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['TCGplayer Id', 'Product Line', 'Set Name', 'Product Name', 'Title', 'Number', 'Rarity', 'Condition', 'TCG Market Price', 'TCG Direct Low', 'TCG Low Price With Shipping', 'TCG Low Price', 'Total Quantity', 'Add to Quantity', 'TCG Marketplace Price', 'Photo URL'])
        for product in products:
            writer.writerow(product.to_row())


if __name__ == '__main__':
    products = process_csv('TCGSYP.csv')
    for product in products:
        if product.direct_low_price.price_type is PriceType.SOME:
            if product.direct_low_price.price >= product.low_price_with_shipping.price:
                product.to_direct_low_with_multiplier(1)
            else:
                product.to_low_with_shipping_with_multiplier(1)
        elif product.low_price_with_shipping.price_type is PriceType.SOME:
            product.to_low_with_shipping_with_multiplier(1.1)
            product.round_to_99()
        if product.marketplace_price.price_type is PriceType.NONE:
            print(product, 'NO PRICE')

    total = 0
    for product in products:
        total += product.marketplace_price.price * int(product.total_quantity)
    print(total)
    # direct_low = 0
    # low_with_shipping = 0
    # for product in products:
    #     if product.direct_low_price.price_type is PriceType.SOME and product.low_price_with_shipping.price_type is PriceType.SOME:
    #         direct_low += product.direct_low_price.price
    #         low_with_shipping += product.low_price_with_shipping.price
    # print(direct_low)
    # print(low_with_shipping)

    # for product in products:
    #     if product.condition.language is Languages.JAPANESE or product.rarity is Rarity.PRODUCT:
    #         product.to_low_with_shipping()
    #         product.round_to_99()
    #     else:
    #         product.add_to_quantity = -product.total_quantity
    # output_csv('TCGSYPX.csv', products)
