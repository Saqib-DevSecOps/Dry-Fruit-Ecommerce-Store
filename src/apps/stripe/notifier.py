from src.apps.whisper.main import NotificationService


def notify_payout_created(obj):
    """completed"""
    description = f"Withdrawal of {obj.amount} {obj.currency} has been added."

    notifier = NotificationService(description, description, obj, [obj.user])
    notifier.send_app_notification(obj.user)
    notifier.send_email_notification(
        template="stripe/emails/vendor_payout_create.html",
        context={'obj': obj, 'user': obj.user, 'description': description}
    )


def notify_payout_status_changed(obj):
    """completed"""
    description = f"Withdrawal of {obj.amount} {obj.currency} has {obj.status}"

    notifier = NotificationService(description, description, obj, [obj.user])
    notifier.send_app_notification(obj.user)
    notifier.send_email_notification(
        template="stripe/emails/vendor_payout_status.html",
        context={'obj': obj, 'user': obj.user, 'description': description}
    )


def notify_transfer_created(obj):
    """completed"""
    description = f"Amount of {obj.amount} {obj.currency} transferred to your connect account."

    notifier = NotificationService(description, description, obj, [obj.user])
    notifier.send_app_notification(obj.user)
    notifier.send_email_notification(
        template="stripe/emails/vendor_transfer_create.html",
        context={'obj': obj, 'user': obj.user, 'description': description}
    )


def notify_subscriptions_created(obj):
    """completed"""

    description = f"You have successfully subscribed to {obj.stripe_price.product.name} package."

    notifier = NotificationService(description, description, obj, [obj.user])
    notifier.send_app_notification(obj.user)
    notifier.send_email_notification(
        template="stripe/emails/subscription_create.html",
        context={'obj': obj, 'user': obj.user, 'description': description}
    )


def notify_subscriptions_updated(obj):
    """completed"""

    description = f"Your subscription of {obj.stripe_price.product.name} package has been updated."

    notifier = NotificationService(description, description, obj, [obj.user])
    notifier.send_app_notification(obj.user)
    notifier.send_email_notification(
        template="stripe/emails/subscription_update.html",
        context={'obj': obj, 'user': obj.user, 'description': description}
    )