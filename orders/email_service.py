from django.core.mail import send_mail


class EmailService:

    @staticmethod
    def send_order_confirmation(order):

        subject = f"Order Confirmation #{order.id}"

        total_price = order.get_total_price()
        delivery_date = order.get_estimated_delivery()

        items_text = ""
        for item in order.items.all():
            items_text += f"- {item.product.name} x {item.quantity} = {item.price}\n"

        message = f"""
Thank you for your order!

Order ID: {order.id}

Items:
{items_text}

Total Price: {total_price}

Estimated Delivery: {delivery_date.strftime('%Y-%m-%d')}

We will notify you when your order is shipped.
"""

        send_mail(
            subject=subject,
            message=message,
            from_email="your_email@yourshop.com",
            recipient_list=[order.user.email],
            fail_silently=False,
        )