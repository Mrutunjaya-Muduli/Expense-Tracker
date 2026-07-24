from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    currency = models.CharField(max_length=10, default='₹')

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def avatar_url(self):
        try:
            if self.avatar and self.avatar.name != 'avatars/default.png':
                return self.avatar.url
        except Exception:
            pass
        return f"https://ui-avatars.com/api/?name={self.user.username}&background=6366f1&color=fff&bold=true"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()


