from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import RegisteredUser

@receiver(post_save, sender=User)
def create_registered_user(sender, instance, created, **kwargs):
    if created:
        try:
            print(f"✅ Signal triggered for {instance.username}")
            RegisteredUser.objects.create(
                user=instance,
                email=instance.email
            )
        except Exception as e:
            print("❌ Error in signal while creating RegisteredUser:", e)
