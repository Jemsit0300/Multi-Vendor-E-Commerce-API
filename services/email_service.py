from django.core.mail import send_mail


def send_vendor_email(vendor, order):

    send_mail(
        subject=f"New Order #{order.id}",
        message=f"You have a new order. Please check your dashboard.",
        from_email="noreply@shop.com",
        recipient_list=[vendor.email],
    )