import unittest
from franciabasket import FranciaBasket, Order, Receipt, rounding_rule
from decimal import Decimal


class TestReceiptFormatCase(unittest.TestCase):

    def setUp(self):
        self.receipt = Receipt()

    def test_print_empty_receipt(self):
        self.assertEqual("\nSales Taxes: 0.00\nTotal: 0.00",
                         self.receipt.deliver())

    def test_print_two_orders_receipt(self):
        orders = [
            Order('1 book at 10.00'),
            Order('1 book at 10.00')
            ]
        self.receipt.set_orders(orders)
        self.receipt.set_tax(Decimal(2.53))
        self.receipt.set_total(Decimal(11.78))

        self.assertEqual("1 book: 10.00\n1 book: 10.00\nSales Taxes: 2.53\nTotal: 11.78",
                         self.receipt.deliver())


class TestBasketCommunicateWithReceiptCase(unittest.TestCase):

    def setUp(self):
        self.orders = []
        self.tax = Decimal("0.0")
        self.total = Decimal("0.0")
        self.basket = FranciaBasket()

    def set_orders(self, orders):
        self.orders = orders

    def set_tax(self, tax):
        self.tax = tax

    def set_total(self, total):
        self.total = total

    def test_print_receipt_empty_basket(self):

        self.basket.print_receipt(self)

        self.assertEqual(0, len(self.orders))
        self.assertEqual(Decimal('0.0'), self.tax)
        self.assertEqual(Decimal('0.0'), self.total)

    def test_print_receipt_two_no_taxed_items(self):
        self.basket.add_item('1 book at 10.02')
        self.basket.add_item('1 book at 10.08')

        self.basket.print_receipt(self)

        self.assertEqual(2, len(self.orders))
        self.assertEqual(Decimal('0.0'), self.tax)
        self.assertEqual(Decimal('20.10'), self.total)

    def test_print_receipt_taxed_items(self):
        self.basket.add_item('1 music CD at 10.00')
        self.basket.add_item('1 music CD at 10.00')

        self.basket.print_receipt(self)

        self.assertEqual(Decimal('2.0'), self.tax)
        self.assertEqual(Decimal('22.0'), self.total)

    def test_basket_orders_are_safe(self):
        self.basket.print_receipt(self)

        self.orders.append('invalid item')

        self.assertNotEqual(len(self.basket.orders()), len(self.orders))


class TestOrderCase(unittest.TestCase):

    def test_parse_order(self):
        order = Order('13 music CD at 14.99')

        self.assertEqual(13, order.quantity())
        self.assertEqual('music CD', order.description())
        self.assertEqual(Decimal('14.99'), order.price())

    def test_rounding_rule(self):
        self.assertEqual(Decimal('1.00'), rounding_rule(Decimal('1.00')))
        self.assertEqual(Decimal('1.05'), rounding_rule(Decimal('1.01')))
        self.assertEqual(Decimal('1.10'), rounding_rule(Decimal('1.06')))

    def test_order_taxes(self):
        order = Order('13 music CD at 14.99')
        price = Decimal('14.99')
        tax = rounding_rule(price * Decimal('0.1'))

        self.assertEqual(tax, order.tax())
        self.assertEqual(price + tax, order.taxed_price())

    def test_order_free(self):
        order = Order('13 book at 14.99')
        self.assertEqual(Decimal('0.00'), order.tax())

    def test_order_free_imported(self):
        order = Order('13 imported book at 10.00')
        price = Decimal('10.00')
        tax = rounding_rule(price * Decimal('0.05') )

        self.assertEqual(tax, order.tax())

    def test_order_imported_and_taxed(self):
        order = Order('1 imported bottle of perfume at 10.00')
        price = Decimal('10.00')
        tax = rounding_rule(price*Decimal('0.05') + price*Decimal('0.10'))
        
        self.assertEqual(tax, order.tax())

    def test_order_tax_check(self):
        order = Order('13 music CD at 14.99')
        self.assertTrue(order.is_taxed())

        order = Order('13 book at 14.99')
        self.assertFalse(order.is_taxed())
        order = Order('13 medical at 14.99')
        self.assertFalse(order.is_taxed())

    def test_order_import_check(self):
        order = Order('13 music CD at 14.99')
        self.assertFalse(order.is_imported())

        order = Order('1 imported box of chocolates at 10.00')
        self.assertTrue(order.is_imported())
