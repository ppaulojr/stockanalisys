"""
Integration tests for ONS S3 data retrieval.

These tests make real network calls to the ONS S3 bucket at
https://ons-aws-prod-opendata.s3.amazonaws.com
and the CKAN API at https://dados.ons.org.br
to verify that the client correctly downloads and parses the CSV data.

Previously these tests could not run due to firewall restrictions.
"""

import requests
import unittest
from ons_integration.client import ONSClient


class TestONSS3Integration(unittest.TestCase):
    """Integration tests for ONS S3 data access"""

    def setUp(self):
        """Initial test setup"""
        self.client = ONSClient(timeout=30)

    def test_download_ear_subsistema_csv(self):
        """Test downloading EAR subsystem CSV from S3"""
        records = self.client.get_ear_subsistema()

        self.assertIsNotNone(records, "Should download EAR data from S3")
        self.assertIsInstance(records, list)
        self.assertGreater(len(records), 0, "Should have at least one record")

        # Check expected columns exist
        first_record = records[0]
        self.assertIn("id_subsistema", first_record)
        self.assertIn("nom_subsistema", first_record)

    def test_download_carga_energia_csv(self):
        """Test downloading energy load CSV from S3"""
        records = self.client.get_carga_energia()

        self.assertIsNotNone(records, "Should download load data from S3")
        self.assertIsInstance(records, list)
        self.assertGreater(len(records), 0, "Should have at least one record")

        # Check expected columns exist
        first_record = records[0]
        self.assertIn("id_subsistema", first_record)
        self.assertIn("val_cargaenergiamwmed", first_record)

    def test_get_reservoir_data_from_s3(self):
        """Test full reservoir data retrieval and parsing from S3"""
        result = self.client.get_reservoir_data_from_s3()

        self.assertIsNotNone(result, "Should return parsed reservoir data")
        self.assertIsInstance(result, dict)

        # Should have data for at least some regions
        expected_regions = {"southeast", "south", "northeast", "north"}
        found_regions = set(result.keys()) & expected_regions
        self.assertGreater(len(found_regions), 0, "Should have data for at least one region")

        # Verify structure of each region
        for region in found_regions:
            self.assertIn("level_percent", result[region])
            self.assertIn("capacity_mwmed", result[region])
            self.assertIn("status", result[region])

            # Level should be a reasonable percentage
            level = result[region]["level_percent"]
            self.assertGreater(level, 0)
            self.assertLessEqual(level, 100)

    def test_get_consumption_data_from_s3(self):
        """Test full consumption data retrieval and parsing from S3"""
        result = self.client.get_consumption_data_from_s3()

        self.assertIsNotNone(result, "Should return parsed consumption data")
        self.assertIsInstance(result, dict)

        self.assertIn("current_load_mw", result)
        self.assertIn("regions", result)
        self.assertGreater(result["current_load_mw"], 0, "Load should be positive")

        # Should have data for at least some regions
        regions = result["regions"]
        self.assertGreater(len(regions), 0, "Should have at least one region")

        # Verify percentages sum to approximately 100%
        total_percent = sum(r["percent"] for r in regions.values())
        self.assertAlmostEqual(total_percent, 100.0, places=0)

    def test_download_csv_data_with_previous_year(self):
        """Test downloading CSV data for previous year"""
        records = self.client.get_ear_subsistema(year=2025)

        self.assertIsNotNone(records, "Should download EAR data for 2025")
        self.assertGreater(len(records), 0)


class TestEnergyFetcherIntegration(unittest.TestCase):
    """Integration tests for EnergyDataFetcher with real S3 data"""

    def setUp(self):
        """Initial test setup"""
        from energy_fetcher import EnergyDataFetcher
        self.fetcher = EnergyDataFetcher()

    def test_get_reservoir_data_returns_s3_data(self):
        """Test that get_reservoir_data returns real data from S3"""
        result = self.fetcher.get_reservoir_data()

        self.assertIsNotNone(result)
        self.assertNotIn("error", result, "Should not return an error")
        self.assertIn("data_source", result)

        # Should have region data
        for region in ["southeast", "south", "northeast", "north"]:
            if region in result:
                self.assertIn("level_percent", result[region])

    def test_get_grid_consumption_returns_s3_data(self):
        """Test that get_grid_consumption returns real data from S3"""
        result = self.fetcher.get_grid_consumption()

        self.assertIsNotNone(result)
        self.assertNotIn("error", result, "Should not return an error")
        self.assertIn("data_source", result)
        self.assertIn("current_load_mw", result)


class TestONSCKANIntegration(unittest.TestCase):
    """Integration tests for ONS CKAN API (dados.ons.org.br)"""

    @classmethod
    def setUpClass(cls):
        """Check if CKAN API is reachable before running tests"""
        try:
            r = requests.get(
                "https://dados.ons.org.br/api/3/action/package_list",
                timeout=10,
            )
            cls.ckan_available = r.status_code == 200
        except Exception:
            cls.ckan_available = False

    def setUp(self):
        """Initial test setup"""
        if not self.ckan_available:
            self.skipTest("CKAN API (dados.ons.org.br) is not reachable")
        self.client = ONSClient(timeout=15)

    def test_search_datasets_reservatorio(self):
        """Test searching for reservoir datasets via CKAN API"""
        results = self.client.search_datasets("reservatorio")

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "Should find reservoir datasets")

    def test_search_datasets_carga(self):
        """Test searching for load/consumption datasets via CKAN API"""
        results = self.client.search_datasets("carga")

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "Should find load datasets")

    def test_list_datasets(self):
        """Test listing available datasets from CKAN API"""
        datasets = self.client.list_datasets()

        self.assertIsInstance(datasets, list)
        self.assertGreater(len(datasets), 0, "Should list at least one dataset")


if __name__ == "__main__":
    unittest.main()
