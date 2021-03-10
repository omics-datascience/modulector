from django.test import Client, TestCase
from modulector.tests.data_init import load_test_data

client = Client()


class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_data(cls)

    def __check_empty_pagination(self, response):
        """Checks if fields of response are valid for an empty pagination response"""
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def testMirnaView(self):
        """Tests mirna endpoint"""
        response = client.get('/mirna/', {'mirna': 'ASDAS_SDA@_SDASD'})
        self.assertEqual(response.status_code, 200)

        # Checks all fields
        data = response.data
        self.assertTrue('aliases' in data)
        self.assertTrue('mirna_sequence' in data)
        self.assertTrue('links' in data)

    def testMirnaViewNotFound(self):
        """Tests 404 error for mirna endpoint due to not specify the 'mirna' parameter"""
        response = client.get('/mirna/')
        self.assertEqual(response.status_code, 404)

    def testMirnaInteractionsView(self):
        """Tests mirna-interactions endpoint"""
        response = client.get('/mirna-interactions/', {'mirna': 'ASDAS_SDA@_SDASD'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        # Checks all fields
        first_result = response.data['results'][0]
        self.assertTrue('id' in first_result)
        self.assertTrue('mirna' in first_result)
        self.assertTrue('gene' in first_result)
        self.assertTrue('score' in first_result)
        self.assertTrue('source_name' in first_result)
        self.assertTrue('pubmeds' in first_result)
        self.assertTrue('sources' in first_result)
        self.assertTrue('score_class' in first_result)

    def testMirnaInteractionsViewNotFound(self):
        """Test emtpy pagination for mirna-interactions endpoint"""
        response = client.get('/mirna-interactions/', {'mirna': 'hsa-invalid'})
        self.assertEqual(response.status_code, 200)
        self.__check_empty_pagination(response)

    def testMirnaXGenView(self):
        """Tests mirna-target-interactions endpoint"""
        response = client.get('/mirna-target-interactions/', {'mirna': 'ASDAS_SDA@_SDASD', 'gene': 'GEN_1'})
        self.assertEqual(response.status_code, 200)

        # Checks all fields
        data = response.data
        self.assertTrue('id' in data)
        self.assertTrue('mirna' in data)
        self.assertTrue('gene' in data)
        self.assertTrue('score' in data)
        self.assertTrue('source_name' in data)
        self.assertTrue('pubmeds' in data)
        self.assertTrue('sources' in data)
        self.assertTrue('score_class' in data)

    def testMirnaXGenViewNotFound(self):
        """Tests 404 error for mirna-target-interaction endpoint due to non-existent miRNA and gene"""
        response = client.get('/mirna-target-interactions/', {'mirna': 'hsa-invalid', 'gene': 'gene-invalid'})
        self.assertEqual(response.status_code, 404)

    def testMirnaAliasesView(self):
        """Tests mirna-aliases endpoint"""
        response = client.get('/mirna-aliases/')
        self.assertEqual(response.status_code, 200)

    def testDiseasesView(self):
        """Tests diseases endpoint"""
        response = client.get('/diseases/')
        self.assertEqual(response.status_code, 200)
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

    def testDrugsView(self):
        """Test drugs endpoint"""
        response = client.get('/drugs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        # Checks all fields
        first_result = response.data['results'][0]
        self.assertTrue('id' in first_result)
        self.assertTrue('small_molecule' in first_result)
        self.assertTrue('fda_approved' in first_result)
        self.assertTrue('detection_method' in first_result)
        self.assertTrue('condition' in first_result)
        self.assertTrue('pubmed' in first_result)
        self.assertTrue('reference' in first_result)
        self.assertTrue('expression_pattern' in first_result)
        self.assertTrue('support' in first_result)

    def testDrugsViewNotFound(self):
        """Test emtpy pagination for drugs endpoint"""
        response = client.get('/drugs/',  {'mirna': 'hsa-invalid'})
        self.assertEqual(response.status_code, 200)
        self.__check_empty_pagination(response)

    def testRootView(self):
        """Tests / endpoint"""
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
