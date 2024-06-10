from src.accounts.models import User
from src.apps.whisper.main import NotificationService


def notify_admin_on_order_received():
    for user in User.objects.filter(is_staff=True):
        heading = "Order Received"
        description = "Your received a new order"
        notifier = NotificationService(heading, description, user, [user])
        notifier.send_app_notification(user)


def notify_admin_on_order_completed():
    for user in User.objects.filter(is_staff=True):
        heading = "Order Completed"
        description = "Your Order Has Been Completed"
        notifier = NotificationService(heading, description, user, [user])
        notifier.send_app_notification(user)
