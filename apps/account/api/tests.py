from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


class BaseTestCase(APITestCase):
    def setUp(self):
        self.email = "test@e.mail"
        self.username = "testuser"
        self.password = "password"

        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.token = Token.objects.create(user=self.user)

        self.email2 = "test@e.mail2"
        self.username2 = "testuser2"
        self.password2 = "password2"

        self.user2 = User.objects.create_user(self.username2, self.email2, self.password2)
        self.token2 = Token.objects.create(user=self.user2)


class LoginTestCase(BaseTestCase):
    def test_login(self):
        url = '/api/login/'

        data = {
            "username": self.username,
            "password": self.password
        }

        response = self.client.post(
            url,
            data=data,
            format='json'
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.token.__str__(), response.data["token"])


class ProfileTestCase(APITestCase):
    pass
