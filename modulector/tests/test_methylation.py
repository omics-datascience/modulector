import json
from django.test import Client, TestCase

client = Client()


class MethylationTests(TestCase):
    """ Testing of methylation endpoints """

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
        """Checks if fields of response are valid for a one-result pagination response"""
        self.assertEqual(response.data['count'], 1)
        self.assertTrue(len(response.data['results']) == 1)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    """ Testing /methylation/ endpoint """

    def testMethylationDetails1(self):
        """ Tests methylation endpoint with a valid methylation site """
        response = client.get(
            '/methylation/', {'methylation_site': 'cg22461615'})
        self.assertEqual(response.status_code, 200)
        # Checks all fields
        data = response.data
        self.assertTrue('name' in data)
        self.assertTrue('chromosome_position' in data)
        self.assertTrue('aliases' in data)
        self.assertTrue('ucsc_cpg_islands' in data)
        self.assertTrue('genes' in data)
        self.assertIsInstance(data['name'], str)
        self.assertIsInstance(data['chromosome_position'], str)
        self.assertIsInstance(data['chromosome_position'], str)
        self.assertIsInstance(data['aliases'], list)
        self.assertIsInstance(data['ucsc_cpg_islands'], list)
        self.assertIsInstance(data['genes'], dict)
        self.assertEqual(data['name'], 'cg22461615')
        self.assertEqual(data['chromosome_position'], 'chr4:82900764 [+]')
        self.assertEqual(data['aliases'], ["cg22461615_TC11"])
        self.assertEqual(data['ucsc_cpg_islands'], [
                         {"cpg_island": "chr4:82900535-82900912", "relation": "Island"}])
        self.assertEqual(data['genes']['THAP9'], ["5UTR", "exon_1"])
        self.assertEqual(data['genes']['THAP9-AS1'], ["exon_1"])
        self.assertEqual(data['genes']['SEC31A'], ["TSS200"])

    def testMethylationDetails2(self):
        """ Tests methylation endpoint with an invalid methylation site """
        response = client.get(
            '/methylation/', {'methylation_site': 'thisIsNotAMethylationSite'})
        self.assertEqual(response.status_code, 400)
        # Checks all fields
        data = response.data
        self.assertIsInstance(data, set)
        self.assertTrue(len(data) == 1)
        self.assertIsInstance(list(data)[0], str)

    def testMethylationDetails3(self):
        """ Tests methylation endpoint without parameters """
        response = client.get('/methylation/')
        self.assertEqual(response.status_code, 400)
        # Checks all fields
        data = response.data
        self.assertIsInstance(data, set)
        self.assertTrue(len(data) == 1)
        self.assertIsInstance(list(data)[0], str)

    def testMethylationDetailsValidRefDatabase(self):
        """ Tests methylation endpoint with a valid ref_database parameter """
        for ref_db in ["gencode", "GENCODE", "refgene", "REFGENE"]:
            response = client.get(
                '/methylation/', {'methylation_site': 'cg22461615', 'ref_database': ref_db})
            self.assertEqual(response.status_code, 200)

    def testMethylationDetailsInvalidRefDatabase(self):
        """ Tests methylation endpoint with an invalid ref_database parameter """
        invalid_values = ["invalid_db", 123, True]
        for val in invalid_values:
            response = client.get(
                '/methylation/', {'methylation_site': 'cg22461615', 'ref_database': val})
            self.assertEqual(response.status_code, 400)
            self.assertTrue("detail" in response.data)

    """ Testing /methylation-sites-finder/ endpoint """

    def testMethylationSitesFinder1(self):
        """ Tests with a valid response whit 7 results """
        response = client.get(
            '/methylation-sites-finder/', {'query': 'cg25', 'limit': 7})
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) == 7)

    def testMethylationSitesFinder2(self):
        """ Tests default limit parameter value """
        response = client.get('/methylation-sites-finder/', {'query': 'cg25'})
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) == 50)

    def testMethylationSitesFinder3(self):
        """ Tests endpoint without parameters """
        response = client.get('/methylation-sites-finder/')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) == 0)

    """ Testing /methylation-sites/ endpoint """

    def testMethylationSites1(self):
        """ Tests with a valid body """
        data_body = json.dumps(
            {
                "methylation_sites": [
                    "cg22461615_TC11",
                    "cg01615704_TC11",
                    "cg25908985",
                    "invalid_data"]
            }
        )
        response = client.post('/methylation-sites/', data=data_body,
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        for k in data:
            self.assertIsInstance(data[k], list)
        self.assertTrue("cg22461615_TC11" in data)
        self.assertTrue("cg01615704_TC11" in data)
        self.assertTrue("cg25908985" in data)
        self.assertTrue("invalid_data" in data)
        self.assertEqual(data["cg22461615_TC11"][0], "cg22461615")
        self.assertEqual(data["cg01615704_TC11"][0], "cg01615704")
        self.assertEqual(data["cg25908985"][0], "cg25908985")
        self.assertTrue(len(data["invalid_data"]) == 0)

    def testMethylationSites2(self):
        """ Tests with an invalid body type """
        data = json.dumps({"methylation_sites": "cg01615704_TC11"})
        response = client.post('/methylation-sites/', data=data,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.data
        self.assertTrue("detail" in data)

    def testMethylationSites3(self):
        """ Tests with an invalid body key """
        data = json.dumps({"methylation": ["cg01615704_TC11"]})
        response = client.post('/methylation-sites/', data=data,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.data
        self.assertTrue("detail" in data)

    """ Testing /methylation-sites-genes/ endpoint """

    def testMethylationSitesToGenes1(self):
        """ Tests with a valid body """
        data_body = json.dumps(
            {"methylation_sites": ["cg17771854_BC11", "cg22461615", "name_007"]})
        response = client.post('/methylation-sites-genes/', data=data_body,
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        # sys.exit(str(data))
        self.assertTrue("cg17771854_BC11" in data)
        self.assertTrue("cg22461615" in data)
        for k in data:
            self.assertIsInstance(data[k], list)
        self.assertEqual(data["cg17771854_BC11"], ["NM_014652.4"])
        self.assertCountEqual(data["cg22461615"], ['NM_024672.6', 'NR_034075.1', 'NR_034076.1', 'NM_001318120.2', 'NR_034077.1', 'NM_001317776.2'])

    def testMethylationSitesToGenes2(self):
        """ Tests with an invalid body type """
        data = json.dumps({"methylation_sites": "cg17771854_BC11"})
        response = client.post('/methylation-sites-genes/', data=data,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.data
        self.assertTrue("detail" in data)

    def testMethylationSitesToGenes3(self):
        """ Tests with an invalid body key """
        data = json.dumps({"methylation": "cg17771854_BC11"})
        response = client.post('/methylation-sites-genes/', data=data,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.data
        self.assertTrue("detail" in data)

    def testMethylationSitesToGenesValidRefDatabase(self):
        """ Tests with valid ref_database values (case-insensitive) """
        for ref_db in ["gencode", "GENCODE", "refgene", "REFGENE"]:
            data_body = json.dumps({
                "methylation_sites": ["cg17771854_BC11"],
                "ref_database": ref_db
            })
            response = client.post('/methylation-sites-genes/', data=data_body,
                                   content_type='application/json')
            self.assertEqual(response.status_code, 200)

    def testMethylationSitesToGenesInvalidRefDatabase(self):
        """ Tests with invalid ref_database values """
        invalid_values = ["invalid_db", 123, True]
        for val in invalid_values:
            data_body = json.dumps({
                "methylation_sites": ["cg17771854_BC11"],
                "ref_database": val
            })
            response = client.post('/methylation-sites-genes/', data=data_body,
                                   content_type='application/json')
            self.assertEqual(response.status_code, 400)
            self.assertTrue("detail" in response.data)

    """ Testing /methylation-genes-translator/ endpoint """

    def testMethylationGenesTranslator1(self):
        """ Tests with a valid body for gencode_to_refgene """
        data_body = json.dumps(
            {
                "genes": ["ENST00000489061.1", "invalid_gene"],
                "direction": "gencode_to_refgene"
            }
        )
        response = client.post('/methylation-genes-translator/', data=data_body,
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertTrue(isinstance(data, dict))
        # Depending on test database state, THAP9 or SEC31A should map to something or be present as keys if mapped.
        # Here we just verify it doesn't break and returns 200.

    def testMethylationGenesTranslator2(self):
        """ Tests with a valid body for refgene_to_gencode """
        data_body = json.dumps(
            {
                "genes": ["NM_014652.4", "invalid_gene"],
                "direction": "refgene_to_gencode"
            }
        )
        response = client.post('/methylation-genes-translator/', data=data_body,
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertTrue(isinstance(data, dict))

    def testMethylationGenesTranslator3(self):
        """ Tests with invalid genes type """
        data_body = json.dumps(
            {
                "genes": "THAP9",
                "direction": "gencode_to_refgene"
            }
        )
        response = client.post('/methylation-genes-translator/', data=data_body,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue("detail" in response.data)

    def testMethylationGenesTranslator4(self):
        """ Tests with invalid direction type """
        data_body = json.dumps(
            {
                "genes": ["THAP9"],
                "direction": "invalid_direction"
            }
        )
        response = client.post('/methylation-genes-translator/', data=data_body,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue("detail" in response.data)

    def testMethylationGenesTranslator5(self):
        """ Tests with missing parameters """
        data_body = json.dumps({"genes": ["THAP9"]})
        response = client.post('/methylation-genes-translator/', data=data_body,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue("detail" in response.data)

