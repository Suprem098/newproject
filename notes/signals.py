from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, StudyMaterial, UserSubjectSubscription, Notification

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance, defaults={'role': 'student'})

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        profile = instance.profile
    except Profile.DoesNotExist:
        profile = None
    if profile:
        profile.save()

@receiver(post_save, sender=StudyMaterial)
def notify_users_on_new_study_material(sender, instance, created, **kwargs):
    if created:
        subject = instance.subject
        subscribers = UserSubjectSubscription.objects.filter(subject=subject).select_related('user')
        for subscription in subscribers:
            Notification.objects.create(
                user=subscription.user,
                study_material=instance,
                message=f"New study material '{instance.title}' uploaded in subject '{subject}'."
            )
