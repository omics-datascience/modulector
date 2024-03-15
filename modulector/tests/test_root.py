from django.test import Client, TestCase

client = Client()


class RootTests(TestCase):
    def testRootView(self):
        """Tests / endpoint"""
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
