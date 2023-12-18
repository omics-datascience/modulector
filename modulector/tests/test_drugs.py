from django.test import Client, TestCase

client = Client()


class drugsTests(TestCase):
    def __check_empty_pagination(self, response):
        """Checks if fields of response are valid for an empty pagination response"""
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def __check_one_result_pagination(self, response):
        """Checks if fields of response are valid for an one-result pagination response"""
        self.assertEqual(response.data['count'], 1)
        self.assertTrue(len(response.data['results']) == 1)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def testDrugs(self):
        """Test drugs endpoint"""
        response = client.get('/drugs/', {'mirna': 'miR-378*'})
        self.assertEqual(response.status_code, 200)
        self.__check_one_result_pagination(response)

        # Checks all fields
        data = response.data['results'][0]
        self.assertTrue('id' in data)
        self.assertTrue('small_molecule' in data)
        self.assertTrue('fda_approved' in data)
        self.assertTrue('detection_method' in data)
        self.assertTrue('condition' in data)
        self.assertTrue('pubmed' in data)
        self.assertTrue('reference' in data)
        self.assertTrue('expression_pattern' in data)
        self.assertTrue('support' in data)

    def testDrugsViewNotFound(self):
        """Test emtpy pagination for drugs endpoint"""
        response = client.get('/drugs/',  {'mirna': 'hsa-invalid'})
        self.assertEqual(response.status_code, 200)
        self.__check_empty_pagination(response)
