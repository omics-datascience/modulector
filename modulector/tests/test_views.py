from django.test import Client, TestCase

from modulector.tests.data_init import load_test_data

client = Client()


class ViewTests(TestCase):
    # FIXME: the structure is old, some tests fail
    @classmethod
    def setUpTestData(cls):
        load_test_data(cls)

    def testAdminView(self):
        response = client.get('/admin/')
        self.assertEqual(response.status_code, 302)

    def testSourceView(self):
        response = client.get('/source/')
        self.assertEqual(response.data['count'], 1)
        self.assertIsNotNone(response.data['results'][0]['name'])
        self.assertEqual(response.status_code, 200)

    def testMirnaView(self):
        response = client.get('/mirna/')
        self.assertEqual(response.data['count'], 1)
        self.assertIsNotNone(response.data['results'][0]['mirna_code'])
        self.assertEqual(response.status_code, 200)

    def testMirnaXGenView(self):
        response = client.get('/mirna-target-interactions/', {'mirna': 'ASDAS_SDA@_SDASD'})
        self.assertEqual(response.data['count'], 1)
        self.assertIsNotNone(response.data['results'][0]['gene'])
        self.assertEqual(response.status_code, 200)

    def testMatureMirnaView(self):
        response = client.get('/maturemirna/')
        self.assertEqual(response.status_code, 200)

    def testLinksView(self):
        response = client.get('/links/', {'mirna': 'hsa-test-1'})
        self.assertEqual(len(response.data), 7)
        self.assertIsNotNone(response.data[0]['source'])
        self.assertEqual(response.status_code, 200)

    def testDiseasesView(self):
        response = client.get('/diseases/')
        self.assertEqual(response.data['count'], 1)
        self.assertIsNotNone(response.data['results'][0]['disease'])
        self.assertEqual(response.status_code, 200)

    def testDrugsView(self):
        response = client.get('/drugs/')
        self.assertEqual(response.data['count'], 1)
        self.assertIsNotNone(response.data['results'][0]['mature_mirna'])
        self.assertEqual(response.status_code, 200)

    def testRootView(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
