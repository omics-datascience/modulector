import json
from django.test import Client, TestCase

client = Client()


class miRNATests(TestCase):
    """ Testing of miRNA endpoints """

    def __check_pagination(self, response):
        """check that the response is paginated"""
        self.assertTrue('count' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('previous' in response.data)
        self.assertTrue('results' in response.data)
        self.assertIsInstance(response.data['results'], list)
        self.assertIsInstance(response.data['count'], int)

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

    """ Testing /mirna/ endpoint """

    def testMirnaList1(self):
        """Tests mirna endpoint with a invalid mirna"""
        response = client.get('/mirna/', {'mirna': 'goku_rules'})
        self.assertEqual(response.status_code, 404)
        # Checks all fields
        data = response.data
        self.assertTrue('detail' in data)

    def testMirnaList2(self):
        """Tests mirna endpoint with a valid mirna"""
        response = client.get('/mirna/', {'mirna': 'hsa-miR-548ai'})
        self.assertEqual(response.status_code, 200)
        # Checks all fields
        data = response.data
        self.assertTrue('aliases' in data)
        self.assertIsInstance(data['aliases'], list)
        self.assertTrue("MIMAT0018989" in data['aliases'])

        self.assertTrue('mirna_sequence' in data)
        self.assertIsInstance(data['mirna_sequence'], str)
        self.assertEqual(data['mirna_sequence'], "AAAGGUAAUUGCAGUUUUUCCC")

        self.assertTrue('mirbase_accession_id' in data)
        self.assertIsInstance(data['mirbase_accession_id'], str)
        self.assertEqual(data['mirbase_accession_id'], "MIMAT0018989")

        self.assertTrue('links' in data)
        self.assertIsInstance(data['links'], list)
        self.assertTrue(len(data['links']) == 1)
        self.assertIsInstance(data['links'][0], dict)
        self.assertTrue('source' in data['links'][0])
        self.assertTrue('url' in data['links'][0])
        self.assertIsInstance(data['links'][0]['source'], str)
        self.assertIsInstance(data['links'][0]['url'], str)

    def testMirnaList3(self):
        """Tests 404 error for mirna endpoint due to not specify the 'mirna' parameter"""
        response = client.get('/mirna/')
        self.assertEqual(response.status_code, 404)

    """ Testing /mirna-target-interactions/ endpoint """

    def testMirnaTargetInteractions1(self):
        """Tests with a invalid mirna"""
        response = client.get(
            '/mirna-target-interactions/', {'mirna': 'goku_capo'})
        self.assertEqual(response.status_code, 200)
        self.__check_pagination(response)
        self.__check_empty_pagination(response)

    def testMirnaTargetInteractions2(self):
        """Tests with a valid mirna and gene"""
        response = client.get(
            '/mirna-target-interactions/', {'mirna': 'hsa-miR-891a-5p', 'gene': 'EGFR'})
        self.assertEqual(response.status_code, 200)
        self.__check_pagination(response)
        self.__check_one_result_pagination(response)
        # Checks all fields
        data = response.data['results'][0]
        self.assertIsInstance(data, dict)

        self.assertTrue('id' in data)
        self.assertIsInstance(data['id'], int)

        self.assertTrue('mirna' in data)
        self.assertIsInstance(data['mirna'], str)

        self.assertTrue('gene' in data)
        self.assertIsInstance(data['gene'], str)

        self.assertTrue('score' in data)
        self.assertIsInstance(data['score'], str)

        self.assertTrue('source_name' in data)
        self.assertIsInstance(data['source_name'], str)

        self.assertTrue('pubmeds' in data)
        self.assertIsInstance(data['pubmeds'], set)

        self.assertTrue('sources' in data)
        self.assertIsInstance(data['sources'], list)

        self.assertTrue('score_class' in data)
        self.assertIsInstance(data['score_class'], str)

    def testMirnaTargetInteractions3(self):
        """Tests 400 error for mirna endpoint due to not specify parameters"""
        response = client.get('/mirna-target-interactions/')
        self.assertEqual(response.status_code, 400)

    """ Testing /mirna-aliases/ endpoint """

    def testMirnaAliases1(self):
        """ Test the entire mirna-aliases/ endpoint since it does not receive parameters """
        response = client.get('/mirna-aliases/')
        self.assertEqual(response.status_code, 200)
        self.__check_pagination(response)

    """ Testing /mirna-codes/ endpoint """

    def testMirnaCodes1(self):
        """ Tests with a valid body """
        data = json.dumps({"mirna_codes": ["name_01", "Hsa-Mir-935-v2_5p*",
                                           "MIMAT0000066",
                                           "MI0026417",
                                           "hsa-let-7e-5p"]
                           })
        response = client.post('/mirna-codes/', data=data,
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertTrue("name_01" in data)
        self.assertTrue("Hsa-Mir-935-v2_5p*" in data)
        self.assertTrue("MIMAT0000066" in data)
        self.assertTrue("MI0026417" in data)
        self.assertTrue("hsa-let-7e-5p" in data)
        self.assertIsNone(data["name_01"])
        self.assertIsNone(data["Hsa-Mir-935-v2_5p*"])
        self.assertEqual(data["MIMAT0000066"], "MIMAT0000066")
        self.assertEqual(data["MI0026417"], "MI0026417")
        self.assertEqual(data["hsa-let-7e-5p"], "MIMAT0000066")

    def testMirnaCodes2(self):
        """ Tests with a invalid body type """
        data = json.dumps({"mirna_codes": "Hsa-Mir-935-v2_5p*"})
        response = client.post('/mirna-codes/', data=data,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.data
        self.assertTrue("detail" in data)

    def testMirnaCodes3(self):
        """ Tests with a invalid body key """
        data = json.dumps({"mirna": ["Hsa-Mir-935-v2_5p*"]})
        response = client.post('/mirna-codes/', data=data,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.data
        self.assertTrue("detail" in data)

    """ Testing /mirna-codes-finder/ endpoint """

    def testMirnaCodesFinder1(self):
        """ Tests with a valid response whit 7 results """
        response = client.get(
            '/mirna-codes-finder/', {'query': 'hsa-', 'limit': 7})
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) == 7)

    def testMirnaCodesFinder2(self):
        """ Tests default limit parameter value """
        response = client.get('/mirna-codes-finder/', {'query': 'hsa-'})
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) == 50)

    def testMirnaCodesFinder3(self):
        """ Tests endpoint without parameters """
        response = client.get('/mirna-codes-finder/')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) == 0)
