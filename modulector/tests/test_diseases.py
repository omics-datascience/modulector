from django.test import Client, TestCase

client = Client()


class DiseaseTests(TestCase):
    def __check_empty_pagination(self, response):
        """Checks if fields of response are valid for an empty pagination response"""
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def testDiseasesView(self):
        """ Test the disease endpoint for a valid mirna """
        response = client.get('/diseases/', {"mirna": "hsa-miR-6511b"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)
        self.assertTrue(len(response.data['results']) == 3)
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
