"""
Tests for the CCEE client
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from ccee_client import CCEEClient


class TestCCEEClient(unittest.TestCase):
    """Tests for the CCEE client"""

    def setUp(self):
        """Set up test fixtures"""
        self.client = CCEEClient(timeout=10)

    def test_init(self):
        """Test client initialization"""
        self.assertEqual(self.client.timeout, 10)
        self.assertIsNotNone(self.client.session)
        # User-Agent must look like a real browser so that Akamai/WAF does not
        # return 403 Forbidden for programmatic requests.
        ua = self.client.session.headers["User-Agent"]
        self.assertIn("Mozilla/5.0", ua)
        self.assertNotIn("StockAnalysys", ua)

    def test_session_has_browser_like_headers(self):
        """Test that session headers mimic a real browser to avoid WAF blocks"""
        headers = self.client.session.headers
        self.assertIn("Accept", headers)
        self.assertIn("Accept-Language", headers)
        self.assertIn("Referer", headers)
        self.assertIn("dadosabertos.ccee.org.br", headers["Referer"])

    def test_base_url(self):
        """Test that the base URL points to CCEE Dados Abertos"""
        self.assertIn("dadosabertos.ccee.org.br", CCEEClient.BASE_URL)

    def test_session_has_retry_adapter(self):
        """Test that the session has retry configured"""
        adapter = self.client.session.get_adapter("https://example.com")
        self.assertEqual(adapter.max_retries.total, 3)
        self.assertEqual(adapter.max_retries.backoff_factor, 1)
        self.assertIn(429, adapter.max_retries.status_forcelist)
        self.assertIn(503, adapter.max_retries.status_forcelist)

    def test_fixture_loading_disabled_by_default(self):
        """Test that fixtures are not used by default"""
        self.assertFalse(self.client.use_fixtures)

    def test_fixture_loading_enabled_via_constructor(self):
        """Test enabling fixtures via constructor"""
        client = CCEEClient(use_fixtures=True, fixtures_path="/tmp/fixtures")
        self.assertTrue(client.use_fixtures)
        self.assertEqual(client.fixtures_path, "/tmp/fixtures")

    @patch('ccee_client.requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "result": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client._make_request("package_show", {"id": "pld_horario"})

        self.assertTrue(result["success"])

    @patch('ccee_client.requests.Session.get')
    def test_make_request_failure(self, mock_get):
        """Test failed API request"""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")

        with self.assertRaises(Exception) as context:
            self.client._make_request("package_show", {"id": "pld_horario"})

        self.assertIn("Erro ao acessar API da CCEE", str(context.exception))

    @patch.object(CCEEClient, '_make_request')
    def test_get_dataset_info(self, mock_request):
        """Test getting dataset info"""
        mock_request.return_value = {
            "success": True,
            "result": {
                "id": "pld_horario",
                "name": "pld_horario",
                "title": "PLD Horário",
                "resources": []
            }
        }

        info = self.client.get_dataset_info("pld_horario")

        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "pld_horario")

    @patch.object(CCEEClient, '_make_request')
    def test_get_resource_data(self, mock_request):
        """Test getting resource data"""
        mock_request.return_value = {
            "success": True,
            "result": {
                "records": [
                    {
                        "dat_referencia": "2025-02-20",
                        "id_subsistema": "SE",
                        "val_pld": "145.32"
                    }
                ]
            }
        }

        records = self.client.get_resource_data("test-resource-id", limit=10)

        self.assertIsNotNone(records)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["val_pld"], "145.32")

    def test_parse_pld_records_empty(self):
        """Test parsing empty records returns None"""
        result = self.client._parse_pld_records([])
        self.assertIsNone(result)

    def test_parse_pld_records_valid(self):
        """Test parsing valid PLD records"""
        records = [
            {
                "dat_referencia": "2025-02-20",
                "id_subsistema": "SE",
                "val_pld": "145.32"
            },
            {
                "dat_referencia": "2025-02-20",
                "id_subsistema": "S",
                "val_pld": "138.75"
            },
            {
                "dat_referencia": "2025-02-20",
                "id_subsistema": "NE",
                "val_pld": "152.18"
            },
            {
                "dat_referencia": "2025-02-20",
                "id_subsistema": "N",
                "val_pld": "148.90"
            },
        ]

        result = self.client._parse_pld_records(records)

        self.assertIsNotNone(result)
        self.assertIn("southeast", result)
        self.assertIn("south", result)
        self.assertIn("northeast", result)
        self.assertIn("north", result)
        self.assertEqual(result["southeast"]["price"], 145.32)
        self.assertEqual(result["southeast"]["submercado"], "SE/CO")
        self.assertEqual(result["southeast"]["currency"], "BRL/MWh")
        self.assertEqual(result["south"]["price"], 138.75)
        self.assertEqual(result["northeast"]["price"], 152.18)
        self.assertEqual(result["north"]["price"], 148.90)
        self.assertEqual(result["data_source"], "CCEE Dados Abertos")

    def test_parse_pld_records_with_comma_decimal(self):
        """Test parsing PLD records with comma as decimal separator"""
        records = [
            {
                "dat_referencia": "2025-02-20",
                "id_subsistema": "SE",
                "val_pld": "145,32"
            },
        ]

        result = self.client._parse_pld_records(records)

        self.assertIsNotNone(result)
        self.assertEqual(result["southeast"]["price"], 145.32)

    def test_parse_pld_records_latest_date_wins(self):
        """Test that the latest date record is used for each submarket"""
        records = [
            {
                "dat_referencia": "2025-02-18",
                "id_subsistema": "SE",
                "val_pld": "100.00"
            },
            {
                "dat_referencia": "2025-02-20",
                "id_subsistema": "SE",
                "val_pld": "150.00"
            },
        ]

        result = self.client._parse_pld_records(records)

        self.assertIsNotNone(result)
        self.assertEqual(result["southeast"]["price"], 150.00)

    def test_parse_pld_records_daily_average(self):
        """Test that multiple hourly records on the same day are averaged"""
        records = [
            {
                "dat_referencia": "2025-02-20",
                "hora": 1,
                "id_subsistema": "SE",
                "val_pld": "100.00"
            },
            {
                "dat_referencia": "2025-02-20",
                "hora": 2,
                "id_subsistema": "SE",
                "val_pld": "200.00"
            },
            {
                "dat_referencia": "2025-02-20",
                "hora": 3,
                "id_subsistema": "SE",
                "val_pld": "300.00"
            },
        ]

        result = self.client._parse_pld_records(records)

        self.assertIsNotNone(result)
        # Average of 100, 200, 300 = 200
        self.assertEqual(result["southeast"]["price"], 200.00)

    def test_parse_pld_records_daily_average_ignores_older_dates(self):
        """Test that daily average only uses the most recent date"""
        records = [
            {
                "dat_referencia": "2025-02-18",
                "hora": 1,
                "id_subsistema": "SE",
                "val_pld": "500.00"
            },
            {
                "dat_referencia": "2025-02-20",
                "hora": 1,
                "id_subsistema": "SE",
                "val_pld": "100.00"
            },
            {
                "dat_referencia": "2025-02-20",
                "hora": 2,
                "id_subsistema": "SE",
                "val_pld": "200.00"
            },
        ]

        result = self.client._parse_pld_records(records)

        self.assertIsNotNone(result)
        # Average of 100, 200 from 2025-02-20 only (not the 500 from 02-18)
        self.assertEqual(result["southeast"]["price"], 150.00)

    def test_parse_pld_records_alternative_field_names(self):
        """Test parsing with alternative field names"""
        records = [
            {
                "dat_referencia": "2025-02-20",
                "nom_subsistema": "SUDESTE",
                "val_pld_medio": "145.32"
            },
        ]

        result = self.client._parse_pld_records(records)

        self.assertIsNotNone(result)
        self.assertEqual(result["southeast"]["price"], 145.32)

    @patch.object(CCEEClient, 'get_dataset_info')
    @patch.object(CCEEClient, 'get_resource_data')
    def test_get_pld_data_success(self, mock_resource_data, mock_dataset_info):
        """Test successful PLD data retrieval"""
        mock_dataset_info.return_value = {
            "id": "pld_horario",
            "resources": [
                {"id": "resource-2024", "name": "PLD_HORARIO_2024"},
                {"id": "resource-2025", "name": "PLD_HORARIO_2025"},
            ]
        }
        mock_resource_data.return_value = [
            {
                "dat_referencia": "2025-02-20",
                "id_subsistema": "SE",
                "val_pld": "145.32"
            },
            {
                "dat_referencia": "2025-02-20",
                "id_subsistema": "S",
                "val_pld": "138.75"
            },
        ]

        result = self.client.get_pld_data()

        self.assertIsNotNone(result)
        self.assertIn("southeast", result)
        self.assertIn("south", result)
        self.assertEqual(result["data_source"], "CCEE Dados Abertos")

    @patch.object(CCEEClient, 'get_dataset_info')
    def test_get_pld_data_no_dataset(self, mock_dataset_info):
        """Test PLD data retrieval when dataset is not available"""
        mock_dataset_info.return_value = None

        result = self.client.get_pld_data()

        self.assertIsNone(result)

    @patch.object(CCEEClient, 'get_dataset_info')
    def test_get_pld_data_no_resources(self, mock_dataset_info):
        """Test PLD data retrieval when no resources exist"""
        mock_dataset_info.return_value = {
            "id": "pld_horario",
            "resources": []
        }

        result = self.client.get_pld_data()

        self.assertIsNone(result)


class TestEnergyFetcherPLD(unittest.TestCase):
    """Tests for EnergyDataFetcher PLD integration with CCEE"""

    @patch('energy_fetcher.CCEEClient')
    @patch('energy_fetcher.ONSClient')
    def test_get_pld_prices_uses_ccee_client(self, mock_ons_cls, mock_ccee_cls):
        """Test that get_pld_prices tries CCEE client first"""
        mock_ccee_instance = mock_ccee_cls.return_value
        mock_ccee_instance.get_pld_data.return_value = {
            'southeast': {
                'price': 200.00,
                'submercado': 'SE/CO',
                'currency': 'BRL/MWh',
                'timestamp': '2025-02-20'
            },
            'data_source': 'CCEE Dados Abertos',
            'note': 'Real-time PLD data from CCEE'
        }

        from energy_fetcher import EnergyDataFetcher
        fetcher = EnergyDataFetcher()
        result = fetcher.get_pld_prices()

        self.assertEqual(result['southeast']['price'], 200.00)
        self.assertEqual(result['data_source'], 'CCEE Dados Abertos')

    @patch('energy_fetcher.CCEEClient')
    @patch('energy_fetcher.ONSClient')
    def test_get_pld_prices_fallback(self, mock_ons_cls, mock_ccee_cls):
        """Test that get_pld_prices falls back when CCEE is unavailable"""
        mock_ccee_instance = mock_ccee_cls.return_value
        mock_ccee_instance.get_pld_data.return_value = None

        from energy_fetcher import EnergyDataFetcher
        fetcher = EnergyDataFetcher()
        result = fetcher.get_pld_prices()

        self.assertIn('southeast', result)
        self.assertIn('south', result)
        self.assertIn('northeast', result)
        self.assertIn('north', result)
        self.assertEqual(result['data_source'], 'Fallback data')


class TestCCEEClientFixtures(unittest.TestCase):
    """Tests for CCEE client using fixture files"""

    def setUp(self):
        """Set up client with fixtures"""
        import os
        self.fixtures_path = os.path.join(
            os.path.dirname(__file__), "fixtures"
        )
        self.client = CCEEClient(
            use_fixtures=True,
            fixtures_path=self.fixtures_path
        )

    def test_fixture_loading_enabled(self):
        """Test that fixtures are enabled"""
        self.assertTrue(self.client.use_fixtures)

    def test_get_dataset_info_from_fixture(self):
        """Test getting PLD dataset info from fixture"""
        dataset = self.client.get_dataset_info("pld_horario")

        self.assertIsNotNone(dataset)
        self.assertEqual(dataset["name"], "pld_horario")
        self.assertIn("resources", dataset)
        self.assertEqual(len(dataset["resources"]), 2)

    def test_get_resource_data_from_fixture(self):
        """Test getting PLD resource data from fixture"""
        records = self.client.get_resource_data("ccee-pld-horario-2025")

        self.assertIsNotNone(records)
        self.assertGreater(len(records), 0)
        # Check structure of first record
        first = records[0]
        self.assertIn("dat_referencia", first)
        self.assertIn("id_subsistema", first)
        self.assertIn("val_pld", first)

    def test_get_pld_data_full_workflow_with_fixtures(self):
        """Test full PLD data retrieval workflow using fixtures"""
        result = self.client.get_pld_data()

        self.assertIsNotNone(result)
        self.assertIn("southeast", result)
        self.assertIn("south", result)
        self.assertIn("northeast", result)
        self.assertIn("north", result)

        # Verify daily average prices from fixture data
        # Each submarket has hourly values 50, 60, 70 on the latest date → average = 60.00
        self.assertEqual(result["southeast"]["price"], 60.00)
        self.assertEqual(result["southeast"]["submercado"], "SE/CO")
        self.assertEqual(result["south"]["price"], 60.00)
        self.assertEqual(result["northeast"]["price"], 60.00)
        self.assertEqual(result["north"]["price"], 60.00)
        self.assertEqual(result["data_source"], "CCEE Dados Abertos")

    def test_fixture_raises_error_when_not_found(self):
        """Test that missing fixture raises error when fixtures are enabled"""
        with self.assertRaises(Exception):
            self.client._make_request("nonexistent_endpoint")


if __name__ == "__main__":
    unittest.main()
