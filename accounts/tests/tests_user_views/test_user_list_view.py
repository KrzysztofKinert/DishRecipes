import math
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

class UserListViewTests(TestCase):
    num_of_users = 11
    paginate_by = 5
    user_list_template = "users/user_list.html"

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        for i in range(1, cls.num_of_users+1):
            User.objects.create_user(username=f"Test{i}", email=f"test{i}@test.com", password="Test12345")

    def test_accounts_redirects_to_users(self):
        response = self.client.get("/accounts/")
        self.assertRedirects(
            response,
            "/accounts/users/",
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_get_user_list(self):
        response = self.client.get("/accounts/users/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.user_list_template)
        self.assertContains(response, "DishRecipes users", html=True)

    def test_user_list_shows_all_users(self):
        response = self.client.get("/accounts/users/")
        self.assertEqual(response.context_data["paginator"].count, self.num_of_users)

    def test_user_list_default_pagination(self):
        response = self.client.get("/accounts/users/")
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.count, self.num_of_users)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_users / self.paginate_by))

    def test_user_list_set_paginate_by(self):
        response = self.client.get("/accounts/users/", data={"paginate_by": "5"})
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.per_page, 5)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_users / 5))
        self.assertContains(response, '<option selected value="5">5</option>', html=True)
        response = self.client.get("/accounts/users/", data={"paginate_by": "10"})
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.per_page, 10)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_users / 10))
        self.assertContains(response, '<option selected value="10">10</option>', html=True)
        response = self.client.get("/accounts/users/", data={"paginate_by": "25"})
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.per_page, 25)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_users / 25))
        self.assertContains(response, '<option selected value="25">25</option>', html=True)
        response = self.client.get("/accounts/users/", data={"paginate_by": "50"})
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.per_page, 50)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_users / 50))
        self.assertContains(response, '<option selected value="50">50</option>', html=True)

    def user_list_set_page_and_paginate_by(self, page, paginate_by):
        max_page = math.ceil(self.num_of_users / paginate_by)
        if paginate_by>self.num_of_users:
            prev_buttons_count = 0
            next_buttons_count = 0
        elif page==1:
            prev_buttons_count = 0
            next_buttons_count = 2
        elif page==max_page:
            prev_buttons_count = 2
            next_buttons_count = 0
        else:
            prev_buttons_count = 2
            next_buttons_count = 2
        response = self.client.get("/accounts/users/", data={"page": f"{page}", "paginate_by": f"{paginate_by}"})
        self.assertContains(response, f"Page {page} of {max_page}", html=True)
        self.assertContains(response, f'<button class="page-link" type="submit" name="page" value="1">&laquo; first</button>', prev_buttons_count, html=True)
        self.assertContains(response, f'<button class="page-link" type="submit" name="page" value="{page-1}">previous</button>', prev_buttons_count, html=True)
        self.assertContains(response, f'<button class="page-link" type="submit" name="page" value="{page+1}">next</button>', next_buttons_count, html=True)
        self.assertContains(response, f'<button class="page-link" type="submit" name="page" value="{max_page}">last &raquo;</button>', next_buttons_count, html=True)

    def test_user_list_pagination(self):
        paginate_by_list = [5, 10, 25, 50]
        for paginate_by in paginate_by_list:
            max_page = math.ceil(self.num_of_users / paginate_by)
            for page in range(1, max_page + 1):
                self.user_list_set_page_and_paginate_by(page, paginate_by)

    def test_user_list_set_only_paginate_by_sets_page_to_1(self):
        response = self.client.get("/accounts/users/", data={"page":"2", "paginate_by": "5"})
        self.assertContains(response, f"Page 2 of {math.ceil(self.num_of_users / 5)}", html=True)
        response = self.client.get("/accounts/users/", data={"paginate_by": "10"})
        self.assertContains(response, f"Page 1 of {math.ceil(self.num_of_users / 10)}", html=True)
        response = self.client.get("/accounts/users/", data={"page":"2", "paginate_by": "10"})
        self.assertContains(response, f"Page 2 of {math.ceil(self.num_of_users / 10)}", html=True)
        response = self.client.get("/accounts/users/", data={"paginate_by": "5"})
        self.assertContains(response, f"Page 1 of {math.ceil(self.num_of_users / 5)}", html=True)

    def test_user_list_shows_user_summary_list(self):
        response = self.client.get("/accounts/users/", data={"paginate_by": "25"})
        for i in range(self.num_of_users):
            user = get_user_model().objects.get(pk=i+1)
            self.assertContains(response, f'<a href="/accounts/users/{user.get_username()}/">{user.get_username()}</a>', html=True)
            self.assertContains(response, f"<p>Joined: {user.date_joined.strftime('%b %d, %Y')}</p>", html=True)