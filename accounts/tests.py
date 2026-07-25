from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import Profile
from .forms import ProfileUpdateForm

class AccountsModelTest(TestCase):
    def test_profile_auto_creation(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.currency, '₹')

class ProfileUpdateFormTest(TestCase):
    def test_clean_avatar_valid(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        avatar = SimpleUploadedFile("small.gif", small_gif, content_type="image/gif")
        form = ProfileUpdateForm(data={'phone': '1234567890', 'currency': '$'}, files={'avatar': avatar})
        self.assertTrue(form.is_valid())

    def test_clean_avatar_too_large(self):
        from io import BytesIO
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_io.write(b'\x00' * (2 * 1024 * 1024 + 1))
        img_io.seek(0)
        avatar = SimpleUploadedFile("large.jpg", img_io.read(), content_type="image/jpeg")
        form = ProfileUpdateForm(data={'phone': '1234567890', 'currency': '$'}, files={'avatar': avatar})
        self.assertFalse(form.is_valid())
        self.assertIn('avatar', form.errors)
        self.assertEqual(form.errors['avatar'][0], "Image file too large. Max size is 2MB.")

class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

    def test_upload_avatar_view(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        avatar = SimpleUploadedFile("small.gif", small_gif, content_type="image/gif")
        
        response = self.client.post(reverse('profile'), {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'currency': '$',
            'avatar': avatar
        })
        self.user.profile.refresh_from_db()
        self.assertIsNotNone(self.user.profile.avatar_base64)
        self.assertTrue(self.user.profile.avatar_base64.startswith("data:image/gif;base64,"))
        self.assertEqual(self.user.profile.avatar.name, 'avatars/default.png')

    def test_clear_avatar_view(self):
        # Set up a base64 avatar
        self.user.profile.avatar_base64 = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
        self.user.profile.save()
        
        response = self.client.post(reverse('profile'), {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'currency': '$',
            'clear_avatar': 'true'
        })
        self.user.profile.refresh_from_db()
        self.assertIsNone(self.user.profile.avatar_base64)
