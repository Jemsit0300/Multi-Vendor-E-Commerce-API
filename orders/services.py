import random


class PaymentService:

    @staticmethod
    def process_payment(order, data=None):
        """
        Mock payment logic
        """

        # OPTION 1: Random success
        success = random.random() < 0.7

        # OPTION 2 (optional): card-based simulation
        if data and data.get("card_number"):
            if data["card_number"] == "4242424242424242":
                success = True
            else:
                success = False

        return success