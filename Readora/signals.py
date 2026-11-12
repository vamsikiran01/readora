from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import RegisteredUser

@receiver(post_save, sender=User)
def create_registered_user(sender, instance, created, **kwargs):
    if created:
        try:
            # Check if profile already created manually in view
            if not hasattr(instance, 'registered_profile'):
                role = 'librarian' if instance.is_superuser or instance.is_staff else 'student'
                RegisteredUser.objects.create(
                    user=instance,
                    email=instance.email or f"{instance.username}@library.local",
                    role=role
                )
        except Exception as e:
            print("❌ Error in signal while creating RegisteredUser:", e)
