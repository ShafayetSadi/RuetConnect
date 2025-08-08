from django.test import TestCase

# Create your tests here.


class HomepageTest(TestCase):
    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class AboutpageTest(TestCase):
    def test_aboutpage(self):
        response = self.client.get("/about/")
        self.assertEqual(response.status_code, 200)
