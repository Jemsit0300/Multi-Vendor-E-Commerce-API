import random


class PaymentService:

    @staticmethod
    def process_payment(order, data=None):

        success = random.random() < 0.7

        if data and data.get("card_number"):
            if data["card_number"] == "4242424242424242":
                success = True
            else:
                success = False

        return success