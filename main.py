import csv

from Enums.Headers import Headers
from Enums.Price import PriceType
from Product import Product


def input_csv(filename: str) -> list[Product]:
    products = []
    with open(filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            param_dict = {header.name.lower(): row[header.value] for header in Headers}
            products.append(Product(**param_dict))
    return products


def output_csv(filename: str, products: list[Product]):
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow((header.value for header in Headers))
        for product in products:
            writer.writerow(product.to_row())


def price_products(products: list[Product]):
    for product in products:
        # If the product has a Direct Low price, set it to the highest of that or TCGLow + Shipping
        if product.direct_low_price.type is PriceType.SOME:
            if product.direct_low_price.price >= product.low_price_with_shipping.price:
                product.to_direct_low_with_multiplier(1)
            else:
                product.to_low_with_shipping_with_multiplier(1)
        # Otherwise, set it to 1.1x TCGLow + Shipping
        elif product.low_price_with_shipping.type is PriceType.SOME:
            product.to_low_with_shipping_with_multiplier(1.1)
            product.round_to_99_cents()


def get_total_price(products: list[Product]) -> float:
    return sum((product.marketplace_price.price * int(product.total_quantity) for product in products))


if __name__ == '__main__':
    products_list = input_csv('TCGSYP.csv')
    price_products(products_list)
    print(get_total_price(products_list))
    output_csv('TCGSYPX2.csv', products_list)
