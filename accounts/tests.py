from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile

class AccountsModelTest(TestCase):
    def test_profile_auto_creation(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.currency, '$')
