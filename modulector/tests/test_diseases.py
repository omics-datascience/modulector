from django.test import Client, TestCase

client = Client()


class DiseaseTests(TestCase):
    def __check_empty_pagination(self, response):
        """Checks if fields of response are valid for an empty pagination response"""
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def __check_one_result_pagination(self, response):
        """Checks if fields of response are valid for a one-result pagination response"""
        self.assertEqual(response.data['count'], 1)
        self.assertTrue(len(response.data['results']) == 1)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def testDiseasesView(self):
        """ Test the disease endpoint for a valid mirna """
        response = client.get('/diseases/', {"mirna": "hsa-miR-9500"})
        self.assertEqual(response.status_code, 200)
        self.__check_one_result_pagination(response)
        self.assertEqual(response.data['count'], 1)
        first_result = response.data['results'][0]
        self.assertTrue('id' in first_result)
        self.assertTrue('category' in first_result)
        self.assertTrue('disease' in first_result)
        self.assertTrue('pubmed' in first_result)
        self.assertTrue('description' in first_result)

    def testDiseasesViewNotFound(self):
        """Test emtpy pagination for diseases endpoint"""
        response = client.get('/diseases/', {'mirna': 'hsa-invalid'})
        self.assertEqual(response.status_code, 200)
        self.__check_empty_pagination(response)
