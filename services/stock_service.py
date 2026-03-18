from django.db import transaction


class StockService:

    @staticmethod
    def validate_stock(order):
        """
        Check if all items have enough stock
        """
        for item in order.items.all():
            if item.product.stock < item.quantity:
                return False, item.product.name

        return True, None

    @staticmethod
    @transaction.atomic
    def reduce_stock(order):
        """
        Safely reduce stock (atomic)
        """
        for item in order.items.select_for_update():

            product = item.product

            if product.stock < item.quantity:
                raise Exception(f"{product.name} out of stock")

            product.stock -= item.quantity
            product.save()