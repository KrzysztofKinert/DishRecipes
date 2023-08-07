from http import HTTPStatus
from django.test import TestCase


class SignupViewTests(TestCase):
    def test_get_index(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "recipes/index.html")
        self.assertContains(response, "<p>TODO</p>", html=True, status_code=HTTPStatus.OK)
