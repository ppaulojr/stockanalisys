"""
Tests for fixture loading in ONS client for sandbox/offline testing
"""

import os
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from ons_integration.client import ONSClient


class TestONSClientFixtures(unittest.TestCase):
    """Tests for ONS client fixture loading"""
    
    def setUp(self):
        """Initial test setup"""
        # Get the fixtures path relative to this test file
        self.fixtures_path = Path(__file__).parent / "fixtures"
        
    def test_fixture_loading_disabled_by_default(self):
        """Verify that fixtures are not used by default"""
        client = ONSClient(timeout=10)
        self.assertFalse(client.use_fixtures)
        
    def test_fixture_loading_enabled_via_constructor(self):
        """Test enabling fixtures via constructor parameter"""
        client = ONSClient(timeout=10, fixtures_path=str(self.fixtures_path), use_fixtures=True)
        self.assertTrue(client.use_fixtures)
        self.assertEqual(client.fixtures_path, str(self.fixtures_path))
        
    def test_fixture_loading_via_env_vars(self):
        """Test enabling fixtures via environment variables"""
        with patch.dict(os.environ, {
            'ONS_USE_FIXTURES': 'true',
            'ONS_FIXTURES_PATH': str(self.fixtures_path)
        }):
            client = ONSClient(timeout=10)
            self.assertTrue(client.use_fixtures)
            self.assertEqual(client.fixtures_path, str(self.fixtures_path))
    
    def test_load_fixture_package_search_reservatorio(self):
        """Test loading package_search fixture for reservatorio"""
        client = ONSClient(timeout=10, fixtures_path=str(self.fixtures_path))
        
        fixture = client._load_fixture("package_search", {"q": "reservatorio"})
        
        self.assertIsNotNone(fixture)
        self.assertTrue(fixture.get("success"))
        self.assertIn("result", fixture)
        self.assertIn("results", fixture["result"])
        
    def test_load_fixture_package_search_carga(self):
        """Test loading package_search fixture for carga"""
        client = ONSClient(timeout=10, fixtures_path=str(self.fixtures_path))
        
        fixture = client._load_fixture("package_search", {"q": "carga"})
        
        self.assertIsNotNone(fixture)
        self.assertTrue(fixture.get("success"))
        self.assertIn("result", fixture)
        
    def test_load_fixture_not_found(self):
        """Test that missing fixture returns None"""
        client = ONSClient(timeout=10, fixtures_path=str(self.fixtures_path))
        
        fixture = client._load_fixture("nonexistent_endpoint", {"q": "test"})
        
        self.assertIsNone(fixture)
        
    def test_load_fixture_invalid_path(self):
        """Test that invalid fixtures path returns None"""
        client = ONSClient(timeout=10, fixtures_path="/nonexistent/path")
        
        fixture = client._load_fixture("package_search", {"q": "reservatorio"})
        
        self.assertIsNone(fixture)
    
    def test_search_datasets_with_fixtures(self):
        """Test search_datasets uses fixtures when enabled"""
        with patch.dict(os.environ, {
            'ONS_USE_FIXTURES': 'true',
            'ONS_FIXTURES_PATH': str(self.fixtures_path)
        }):
            client = ONSClient(timeout=10)
            
            # This should use the fixture instead of making a real request
            results = client.search_datasets("reservatorio")
            
            self.assertIsInstance(results, list)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["name"], "ear-subsistema")
    
    def test_search_datasets_carga_with_fixtures(self):
        """Test search_datasets for carga uses fixtures when enabled"""
        with patch.dict(os.environ, {
            'ONS_USE_FIXTURES': 'true',
            'ONS_FIXTURES_PATH': str(self.fixtures_path)
        }):
            client = ONSClient(timeout=10)
            
            results = client.search_datasets("carga")
            
            self.assertIsInstance(results, list)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["name"], "carga-energia")
    
    def test_fixture_raises_error_when_not_found_and_enabled(self):
        """Test that missing fixture raises error when fixtures are enabled"""
        with patch.dict(os.environ, {
            'ONS_USE_FIXTURES': 'true',
            'ONS_FIXTURES_PATH': str(self.fixtures_path)
        }):
            client = ONSClient(timeout=10)
            
            # This should raise an exception because no fixture exists
            with self.assertRaises(Exception) as context:
                client._make_request("nonexistent_endpoint", {"q": "unknown"})
            
            self.assertIn("Fixture not found", str(context.exception))


class TestONSClientFixturesIntegration(unittest.TestCase):
    """Integration tests for fixture-based testing"""
    
    def setUp(self):
        """Initial test setup"""
        self.fixtures_path = Path(__file__).parent / "fixtures"
    
    def test_full_workflow_with_fixtures(self):
        """Test complete reservoir data workflow with fixtures"""
        with patch.dict(os.environ, {
            'ONS_USE_FIXTURES': 'true',
            'ONS_FIXTURES_PATH': str(self.fixtures_path)
        }):
            client = ONSClient(timeout=10)
            
            # Search for datasets
            datasets = client.search_datasets("reservatorio")
            self.assertIsNotNone(datasets)
            self.assertGreater(len(datasets), 0)
            
            # Verify dataset structure
            dataset = datasets[0]
            self.assertIn("name", dataset)
            self.assertIn("resources", dataset)


class TestONSClientS3Fixtures(unittest.TestCase):
    """Tests for S3-based CSV fixture loading"""
    
    def setUp(self):
        """Initial test setup"""
        self.fixtures_path = Path(__file__).parent / "fixtures"
    
    def test_load_csv_fixture_ear_subsistema(self):
        """Test loading EAR subsystem CSV fixture"""
        client = ONSClient(timeout=10, fixtures_path=str(self.fixtures_path), use_fixtures=True)
        
        records = client._load_csv_fixture("ear_subsistema", "EAR_DIARIO_SUBSISTEMA")
        
        self.assertIsNotNone(records)
        self.assertIsInstance(records, list)
        self.assertGreater(len(records), 0)
        
        # Check expected columns
        first_record = records[0]
        self.assertIn("id_subsistema", first_record)
        self.assertIn("nom_subsistema", first_record)
    
    def test_load_csv_fixture_carga_energia(self):
        """Test loading energy load CSV fixture"""
        client = ONSClient(timeout=10, fixtures_path=str(self.fixtures_path), use_fixtures=True)
        
        records = client._load_csv_fixture("carga_energia", "CARGA_ENERGIA")
        
        self.assertIsNotNone(records)
        self.assertIsInstance(records, list)
        self.assertGreater(len(records), 0)
        
        # Check expected columns
        first_record = records[0]
        self.assertIn("id_subsistema", first_record)
        self.assertIn("val_cargaenergiamwmed", first_record)
    
    def test_parse_ear_records(self):
        """Test parsing EAR records into reservoir data"""
        client = ONSClient(timeout=10, fixtures_path=str(self.fixtures_path), use_fixtures=True)
        
        # Load fixture
        records = client._load_csv_fixture("ear_subsistema", "EAR_DIARIO_SUBSISTEMA")
        self.assertIsNotNone(records)
        
        # Parse records
        result = client._parse_ear_records(records)
        
        self.assertIsNotNone(result)
        self.assertIn("southeast", result)
        self.assertIn("south", result)
        self.assertIn("northeast", result)
        self.assertIn("north", result)
        
        # Check structure of each region
        for region in ["southeast", "south", "northeast", "north"]:
            self.assertIn("level_percent", result[region])
            self.assertIn("capacity_mwmed", result[region])
            self.assertIn("status", result[region])
            self.assertIn("timestamp", result[region])
    
    def test_parse_carga_records(self):
        """Test parsing load records into consumption data"""
        client = ONSClient(timeout=10, fixtures_path=str(self.fixtures_path), use_fixtures=True)
        
        # Load fixture
        records = client._load_csv_fixture("carga_energia", "CARGA_ENERGIA")
        self.assertIsNotNone(records)
        
        # Parse records
        result = client._parse_carga_records(records)
        
        self.assertIsNotNone(result)
        self.assertIn("current_load_mw", result)
        self.assertIn("forecast_load_mw", result)
        self.assertIn("regions", result)
        
        # Check regions
        regions = result["regions"]
        self.assertIn("southeast", regions)
        self.assertIn("south", regions)
        
        # Verify percentages sum to ~100%
        total_percent = sum(r["percent"] for r in regions.values())
        self.assertAlmostEqual(total_percent, 100.0, places=0)
    
    def test_get_reservoir_data_from_s3_with_fixtures(self):
        """Test full S3 reservoir data retrieval with fixtures"""
        client = ONSClient(timeout=10, fixtures_path=str(self.fixtures_path), use_fixtures=True)
        
        result = client.get_reservoir_data_from_s3()
        
        self.assertIsNotNone(result)
        self.assertIn("southeast", result)
        
        # Check that level percentages are reasonable
        se_level = result["southeast"]["level_percent"]
        self.assertGreater(se_level, 0)
        self.assertLess(se_level, 100)
    
    def test_get_consumption_data_from_s3_with_fixtures(self):
        """Test full S3 consumption data retrieval with fixtures"""
        client = ONSClient(timeout=10, fixtures_path=str(self.fixtures_path), use_fixtures=True)
        
        result = client.get_consumption_data_from_s3()
        
        self.assertIsNotNone(result)
        self.assertIn("current_load_mw", result)
        self.assertGreater(result["current_load_mw"], 0)


if __name__ == "__main__":
    unittest.main()
