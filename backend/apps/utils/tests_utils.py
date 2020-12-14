import logging
from urllib.parse import urlencode

from django.test import TestCase
from django.urls import reverse

from apps.translations.models import Language
from apps.users.models import User
from apps.utils.tests_query_counter import APIClientWithQueryCounter


class BaseTestCase(TestCase):
    email = 'test@test.lt'
    password = 'testtest'
    credentials = {'email': email, 'password': password}
    user_data = {'email': email, 'password': password,
                 'first_name': 'First', 'last_name': 'Last'}
    auth_url = reverse('login')
    query_limits = {}

    def setUp(self):
        logging.disable(logging.INFO)
        self.language = Language.objects.create(
            name='test',
            code='en'
        )
        self.user = User.objects.create_user(**self.user_data)
        self.user.is_verified = True
        self.user.language = self.language
        self.user.save()
        self.client = APIClientWithQueryCounter(test_case=self)

        # Default query_limits for all project:
        self.query_limits["ANY GET REQUEST"] = 5
        self.query_limits["ANY POST REQUEST"] = 5
        self.query_limits["ANY PUT REQUEST"] = 5
        self.query_limits["ANY DELETE REQUEST"] = 5

    def tearDown(self):
        logging.disable(logging.NOTSET)
        super(BaseTestCase, self).tearDown()

    def authorize(self):
        token = self.client.post(self.auth_url, self.credentials).data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        return self.client

    def get(self, path: str, query_params: dict = None, *args, **kwargs):
        if query_params:
            path += f"?{urlencode(query_params)}"
        return self.authorize().get(path=path, *args, **kwargs)

    def post(self, path: str, data: dict = None, format: str = "json", *args, **kwargs):
        return self.authorize().post(path=path, data=data, format=format, *args, **kwargs)

    def put(self, path: str, data: dict = None, format: str = "json", *args, **kwargs):
        return self.authorize().put(path=path, data=data, format=format, *args, **kwargs)

    def patch(self, path: str, data: dict = None, format: str = "json", *args, **kwargs):
        return self.authorize().patch(path=path, data=data, format=format, *args, **kwargs)
