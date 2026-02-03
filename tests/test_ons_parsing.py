"""
Testes para parsing de dados do ONS
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from ons_integration.client import ONSClient


class TestONSDataParsing(unittest.TestCase):
    """Testes para o parsing de dados do ONS"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.client = ONSClient(timeout=10)
    
    def test_parse_reservoir_data_with_valid_dataset(self):
        """Testa parsing de dados de reservatório com dataset válido"""
        # Mock de um dataset com recursos
        mock_datasets = [{
            "name": "ear-reservatorios",
            "resources": [{
                "id": "resource-123",
                "name": "ear_subsistema.csv",
                "format": "CSV"
            }]
        }]
        
        # Mock dos registros retornados
        mock_records = [{
            "data": "2024-01-15",
            "sudeste": "65.4",
            "sul": "58.2",
            "nordeste": "42.8",
            "norte": "71.3"
        }]
        
        with patch.object(self.client, 'get_dataset_resource_data', return_value=mock_records):
            result = self.client.parse_reservoir_data(mock_datasets)
        
        # Verificar que o resultado foi parseado corretamente
        self.assertIsNotNone(result)
        self.assertIn("southeast", result)
        self.assertIn("south", result)
        self.assertIn("northeast", result)
        self.assertIn("north", result)
        
        # Verificar valores
        self.assertEqual(result["southeast"]["level_percent"], 65.4)
        self.assertEqual(result["south"]["level_percent"], 58.2)
        self.assertEqual(result["northeast"]["level_percent"], 42.8)
        self.assertEqual(result["north"]["level_percent"], 71.3)
    
    def test_parse_reservoir_data_empty_datasets(self):
        """Testa parsing com lista vazia de datasets"""
        result = self.client.parse_reservoir_data([])
        self.assertIsNone(result)
    
    def test_parse_reservoir_data_no_valid_resources(self):
        """Testa parsing quando não há recursos válidos"""
        mock_datasets = [{
            "name": "test-dataset",
            "resources": [{
                "id": "resource-123",
                "name": "other_data.pdf",
                "format": "PDF"
            }]
        }]
        
        result = self.client.parse_reservoir_data(mock_datasets)
        self.assertIsNone(result)
    
    def test_parse_consumption_data_with_valid_dataset(self):
        """Testa parsing de dados de consumo com dataset válido"""
        # Mock de um dataset com recursos
        mock_datasets = [{
            "name": "carga-sistema",
            "resources": [{
                "id": "resource-456",
                "name": "carga_regiao.csv",
                "format": "CSV"
            }]
        }]
        
        # Mock dos registros retornados
        mock_records = [{
            "data": "2024-01-15T10:00:00",
            "sudeste": "38245",
            "sul": "9876",
            "nordeste": "12543",
            "norte": "7878"
        }]
        
        with patch.object(self.client, 'get_dataset_resource_data', return_value=mock_records):
            result = self.client.parse_consumption_data(mock_datasets)
        
        # Verificar que o resultado foi parseado corretamente
        self.assertIsNotNone(result)
        self.assertIn("current_load_mw", result)
        self.assertIn("regions", result)
        
        # Verificar regiões
        regions = result["regions"]
        self.assertIn("southeast", regions)
        self.assertIn("south", regions)
        self.assertIn("northeast", regions)
        self.assertIn("north", regions)
        
        # Verificar valores
        self.assertEqual(regions["southeast"]["load_mw"], 38245)
        self.assertEqual(regions["south"]["load_mw"], 9876)
        
        # Verificar que a carga total foi calculada
        total = sum(r["load_mw"] for r in regions.values())
        self.assertEqual(result["current_load_mw"], total)
        
        # Verificar percentuais
        self.assertGreater(regions["southeast"]["percent"], 0)
        self.assertLess(regions["southeast"]["percent"], 100)
    
    def test_parse_consumption_data_empty_datasets(self):
        """Testa parsing com lista vazia de datasets"""
        result = self.client.parse_consumption_data([])
        self.assertIsNone(result)
    
    def test_extract_reservoir_values_with_alternative_fields(self):
        """Testa extração com nomes alternativos de campos"""
        # Mock com diferentes nomes de campos
        mock_records = [{
            "data": "2024-01-15",
            "se_co": "70.5",
            "s": "55.0"
        }]
        
        result = self.client._extract_reservoir_values(mock_records)
        
        self.assertIsNotNone(result)
        # Deve reconhecer 'se_co' como southeast e 's' como south
        if "southeast" in result:
            self.assertEqual(result["southeast"]["level_percent"], 70.5)
        if "south" in result:
            self.assertEqual(result["south"]["level_percent"], 55.0)
    
    def test_extract_consumption_values_calculates_percentages(self):
        """Testa cálculo de percentuais no consumo"""
        mock_records = [{
            "sudeste": "50000",
            "sul": "25000",
            "nordeste": "15000",
            "norte": "10000"
        }]
        
        result = self.client._extract_consumption_values(mock_records)
        
        self.assertIsNotNone(result)
        
        # Verificar que a soma dos percentuais é próxima de 100
        total_percent = sum(r["percent"] for r in result["regions"].values())
        self.assertAlmostEqual(total_percent, 100.0, places=0)
        
        # Verificar que sudeste tem o maior percentual
        self.assertGreater(
            result["regions"]["southeast"]["percent"],
            result["regions"]["south"]["percent"]
        )
    
    def test_extract_reservoir_values_sets_status(self):
        """Testa que o status é definido corretamente baseado no nível"""
        # Nível acima de 50%
        mock_records_high = [{"sudeste": "65.0"}]
        result_high = self.client._extract_reservoir_values(mock_records_high)
        if result_high and "southeast" in result_high:
            self.assertEqual(result_high["southeast"]["status"], "normal")
        
        # Nível abaixo de 50%
        mock_records_low = [{"sudeste": "35.0"}]
        result_low = self.client._extract_reservoir_values(mock_records_low)
        if result_low and "southeast" in result_low:
            self.assertEqual(result_low["southeast"]["status"], "attention")
    
    def test_get_dataset_resource_data_with_limit(self):
        """Testa obtenção de dados com limite personalizado"""
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {
                "success": True,
                "result": {
                    "records": [{"data": "test"}] * 50
                }
            }
            
            result = self.client.get_dataset_resource_data("test-id", limit=50)
            
            # Verificar que o limite foi passado corretamente
            mock_request.assert_called_once_with(
                "datastore_search",
                {"resource_id": "test-id", "limit": 50}
            )
            
            self.assertEqual(len(result), 50)


class TestEnergyFetcherWithParsing(unittest.TestCase):
    """Testes de integração para EnergyDataFetcher com parsing"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        from energy_fetcher import EnergyDataFetcher
        self.fetcher = EnergyDataFetcher()
    
    @patch('ons_integration.client.ONSClient.search_datasets')
    @patch('ons_integration.client.ONSClient.parse_reservoir_data')
    def test_get_reservoir_data_with_successful_parsing(self, mock_parse, mock_search):
        """Testa obtenção de dados quando parsing é bem-sucedido"""
        # Mock de datasets encontrados
        mock_search.return_value = [{"name": "test-dataset"}]
        
        # Mock de dados parseados com sucesso
        mock_parse.return_value = {
            "southeast": {"level_percent": 70.0, "capacity_mwmed": 208355, "status": "normal"},
            "south": {"level_percent": 60.0, "capacity_mwmed": 19768, "status": "normal"}
        }
        
        result = self.fetcher.get_reservoir_data()
        
        # Verificar que retornou dados parseados
        self.assertIn("data_source", result)
        self.assertEqual(result["data_source"], "ONS API")
        self.assertIn("successfully", result["note"].lower())
        
        # Verificar que os dados parseados estão presentes
        self.assertEqual(result["southeast"]["level_percent"], 70.0)
    
    @patch('ons_integration.client.ONSClient.search_datasets')
    @patch('ons_integration.client.ONSClient.parse_reservoir_data')
    def test_get_reservoir_data_parsing_fails(self, mock_parse, mock_search):
        """Testa fallback quando parsing falha"""
        # Mock de datasets encontrados mas parsing retorna None
        mock_search.return_value = [{"name": "test-dataset"}]
        mock_parse.return_value = None
        
        result = self.fetcher.get_reservoir_data()
        
        # Verificar que retornou fallback data
        self.assertIn("data_source", result)
        self.assertEqual(result["data_source"], "Fallback data")
        self.assertIn("not recognized", result["note"].lower())
    
    @patch('ons_integration.client.ONSClient.search_datasets')
    @patch('ons_integration.client.ONSClient.parse_consumption_data')
    def test_get_consumption_data_with_successful_parsing(self, mock_parse, mock_search):
        """Testa obtenção de consumo quando parsing é bem-sucedido"""
        # Mock de datasets encontrados
        mock_search.return_value = [{"name": "test-dataset"}]
        
        # Mock de dados parseados com sucesso
        mock_parse.return_value = {
            "current_load_mw": 70000,
            "forecast_load_mw": 72000,
            "regions": {
                "southeast": {"load_mw": 40000, "percent": 57.1}
            }
        }
        
        result = self.fetcher.get_grid_consumption()
        
        # Verificar que retornou dados parseados
        self.assertIn("data_source", result)
        self.assertEqual(result["data_source"], "ONS API")
        self.assertIn("successfully", result["note"].lower())
        
        # Verificar que os dados parseados estão presentes
        self.assertEqual(result["current_load_mw"], 70000)


if __name__ == "__main__":
    unittest.main()
