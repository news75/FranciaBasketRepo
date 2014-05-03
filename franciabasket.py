from decimal import Decimal
import math


class FranciaBasket:

    def __init__(self):
        self._orders = []
        self.tax_accumulator = Decimal(0.00)
        self.sales_accumulator = Decimal(0.00)

    def add_item(self, order):
        self._orders.append(Order(order))

    def print_receipt(self, receipt):
        self.evaluate_purchase()
        receipt.set_orders(self.orders())
        receipt.set_tax(self.tax_accumulator)
        receipt.set_total(self.sales_accumulator)      

    def evaluate_purchase(self):
        for order in self._orders:
            self.tax_accumulator += order.tax()

        for order in self._orders:
            self.sales_accumulator += order.taxed_price()

    def orders(self):
        return list(self._orders)

    def tax(self):
        return self.tax_accumulator

    def total(self):
        return self.sales_accumulator


def rounding_rule(value):
    rounding_precision = Decimal('0.05')
    return Decimal(math.ceil(value / rounding_precision)) * \
        rounding_precision.quantize(Decimal('.021'))
    

class Order:

    TAX_FREE_ITEMS = ['book', 'food', 'chocolate', 'medical', 'pills']

    def __init__(self, order, _round = rounding_rule):
        self.order = order.strip()
        self._round = _round
        self._parse()

    def _parse(self):
        _left, _price = self.order.split(' at ')
        _quantity, _description = _left.split(' ', 1)

        self._quantity = _quantity.strip()
        self._description = _description.strip()
        self._price = _price.strip()

    def quantity(self):
        return int(self._quantity)

    def description(self):
        return self._description

    def price(self):
        return Decimal(self._price)

    def taxed_price(self):
        return self.price() + self.tax()

    def tax(self):
        return self._round(self.price() * self._tax_factor())

    def _tax_factor(self):
        percentage = Decimal('0.0')
        if self.is_taxed():
            percentage += self._generic_tax_factor()
        if self.is_imported():
            percentage += self._imported_tax_factor()
        return percentage

    def _generic_tax_factor(self):
        return Decimal('0.1')

    def _imported_tax_factor(self):
        return Decimal('0.05')

    def is_taxed(self):
        return not any([item in self.description() for
                        item in self.TAX_FREE_ITEMS])

    def is_imported(self):
        return 'imported' in self.description()


class Receipt:

    def __init__(self):
        self.tax = Decimal(0.0)
        self.total = Decimal(0.0)
        self.items = []
        self.orders = []

    def set_orders(self, orders):
        self.orders = orders

    def set_tax(self, tax):
        self.tax = tax

    def set_total(self, total):
        self.total = total

    def deliver(self):
        return "%s\nSales Taxes: %.2f\nTotal: %.2f" % (self._header(), self.tax, self.total)

    def _header(self):
        lines = ['%d %s: %.2f' % (order.quantity(),
                 order.description(),
                 order.taxed_price()) for
                 order in self.orders]
        return "\n".join(lines)
