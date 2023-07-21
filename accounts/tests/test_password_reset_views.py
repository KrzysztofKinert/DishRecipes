from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core import mail


class PasswordResetViewsTests(TestCase):
    def test_get_password_reset(self):
        response = self.client.get("/accounts/password_reset/")
        self.assertContains(response, "<h1>Reset password</h1>", html=True, status_code=HTTPStatus.OK)

    def test_post_password_reset_valid_data(self):
        response = self.client.post(
            "/accounts/password_reset/",
            data={"email": "test@test.com"},
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_password_reset_invalid_data(self):
        response = self.client.post(
            "/accounts/password_reset/",
            data={"email": ""},
        )
        self.assertNotEqual(response.status_code, HTTPStatus.FOUND)

    def test_password_reset_forwards_to_done(self):
        response = self.client.post("/accounts/password_reset/", data={"email": "Test@test.com"}, follow=True)
        self.assertRedirects(response, "/accounts/password_reset/done/", status_code=HTTPStatus.FOUND)

    def test_get_password_reset_done(self):
        response = self.client.get("/accounts/password_reset/done/")
        self.assertContains(
            response,
            "We've emailed you instructions for resetting your password.",
            status_code=HTTPStatus.OK,
        )

    def test_password_reset_email_sent_if_address_valid(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.post("/accounts/password_reset/", data={"email": "Test@test.com"}, follow=True)
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_email_not_sent_if_address_invalid(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.post("/accounts/password_reset/", data={"email": "Test2@test.com"}, follow=True)
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_email_content(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.post("/accounts/password_reset/", data={"email": "Test@test.com"}, follow=True)
        protocol = "http"
        domain = "testserver"
        email = mail.outbox[0]
        self.assertIn(f"reset on {domain}", email.body)
        self.assertIn(f"for email: Test@test.com", email.body)
        self.assertIn(f"{protocol}://{domain}/accounts/reset/", email.body)

    def test_get_password_reset_confirm(self):
        response = self.client.get("/accounts/reset/AA/1/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_confirm_valid_token(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.post("/accounts/password_reset/", data={"email": "Test@test.com"}, follow=True)
        uid = mail.outbox[0].body.split("/")[-3]
        token = mail.outbox[0].body.split("/")[-2]
        response = self.client.get(f"/accounts/reset/{uid}/{token}/", follow=True)
        self.assertContains(response, "<h1>Reset password</h1>", html=True, status_code=HTTPStatus.OK)

    def test_password_reset_confirm_invalid_token(self):
        response = self.client.get("/accounts/reset/AA/1/")
        self.assertContains(response, "<h1>Password reset failed</h1>", html=True, status_code=HTTPStatus.OK)

    def test_password_reset_confirm_valid_token_valid_data(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.post("/accounts/password_reset/", data={"email": "Test@test.com"}, follow=True)
        uid = mail.outbox[0].body.split("/")[-3]
        token = mail.outbox[0].body.split("/")[-2]
        response = self.client.post(
            f"/accounts/reset/{uid}/{token}/",
            follow=True,
        )
        self.assertRedirects(
            response,
            f"/accounts/reset/{uid}/set-password/",
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_get_password_reset_set_password_invalid_uid(self):
        response = self.client.get("/accounts/reset/AA/set-password/")
        self.assertContains(response, "<h1>Password reset failed</h1>", html=True, status_code=HTTPStatus.OK)

    def test_get_password_reset_set_password_valid_uid(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.post("/accounts/password_reset/", data={"email": "Test@test.com"}, follow=True)
        uid = mail.outbox[0].body.split("/")[-3]
        token = mail.outbox[0].body.split("/")[-2]
        self.client.post(f"/accounts/reset/{uid}/{token}/", follow=True)
        response = self.client.get(f"/accounts/reset/{uid}/set-password/")
        self.assertContains(response, "<h1>Reset password</h1>", html=True, status_code=HTTPStatus.OK)

    def test_post_password_reset_set_password_valid_data(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.post("/accounts/password_reset/", data={"email": "Test@test.com"}, follow=True)
        uid = mail.outbox[0].body.split("/")[-3]
        token = mail.outbox[0].body.split("/")[-2]
        response = self.client.get(f"/accounts/reset/{uid}/{token}/")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.client.post(
            f"/accounts/reset/{uid}/set-password/", data={"new_password1": "Test54321", "new_password2": "Test54321"}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_password_reset_set_password_invalid_data(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.post("/accounts/password_reset/", data={"email": "Test@test.com"}, follow=True)
        uid = mail.outbox[0].body.split("/")[-3]
        token = mail.outbox[0].body.split("/")[-2]
        self.client.post(f"/accounts/reset/{uid}/{token}/")
        response = self.client.post(
            f"/accounts/reset/{uid}/set-password/", data={"new_password1": "", "new_password2": ""}
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_password_reset_complete(self):
        response = self.client.get("/accounts/reset/done/")
        self.assertContains(response, "<h2>The password has been changed!</h2>", html=True, status_code=HTTPStatus.OK)

    def test_password_reset_integration(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.post("/accounts/password_reset/", data={"email": "Test@test.com"}, follow=True)
        uid = mail.outbox[0].body.split("/")[-3]
        token = mail.outbox[0].body.split("/")[-2]
        self.client.post(f"/accounts/reset/{uid}/{token}/", follow=True)
        self.client.post(
            f"/accounts/reset/{uid}/set-password/",
            data={"new_password1": "Test54321", "new_password2": "Test54321"},
            follow=True,
        )
        login = self.client.login(username="Test", password="Test12345")
        self.assertFalse(login)
        login = self.client.login(username="Test", password="Test54321")
        self.assertTrue(login)
