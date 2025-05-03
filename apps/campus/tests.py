from django.test import SimpleTestCase

# Create your tests here.


class HomepageTest(SimpleTestCase):
    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class AboutpageTest(SimpleTestCase):
    def test_aboutpage(self):
        response = self.client.get("/about/")
        self.assertEqual(response.status_code, 200)
