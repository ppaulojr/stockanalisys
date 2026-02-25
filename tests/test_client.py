"""
Testes para o cliente ONS
"""

import unittest
from unittest.mock import Mock, patch
from ons_integration.client import ONSClient


class TestONSClient(unittest.TestCase):
    """Testes para o cliente ONS"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.client = ONSClient(timeout=10)
    
    def test_init(self):
        """Testa inicialização do cliente"""
        self.assertEqual(self.client.timeout, 10)
        self.assertIsNotNone(self.client.session)
        self.assertEqual(
            self.client.session.headers["User-Agent"],
            "StockAnalysys-ONS-Integration/0.1.0"
        )
    
    def test_s3_base_url(self):
        """Testa que a URL base do S3 aponta para o bucket correto"""
        self.assertIn("ons-aws-prod-opendata", ONSClient.S3_BASE_URL)
        self.assertNotIn("ons-dl-prod-opendata", ONSClient.S3_BASE_URL)
    
    def test_carga_energia_dataset_path(self):
        """Testa que o path do dataset carga_energia usa o sufixo _di"""
        self.assertEqual(ONSClient.DATASET_PATHS["carga_energia"], "carga_energia_di")
    
    def test_session_has_retry_adapter(self):
        """Testa que a sessão tem retry configurado para lidar com erros de rede transitórios"""
        adapter = self.client.session.get_adapter("https://example.com")
        self.assertEqual(adapter.max_retries.total, 3)
        self.assertEqual(adapter.max_retries.backoff_factor, 1)
        self.assertIn(429, adapter.max_retries.status_forcelist)
        self.assertIn(503, adapter.max_retries.status_forcelist)
    
    @patch('ons_integration.client.requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Testa requisição bem-sucedida"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "result": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client._make_request("test_endpoint")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], [])
    
    @patch('ons_integration.client.requests.Session.get')
    def test_make_request_failure(self, mock_get):
        """Testa falha na requisição"""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        with self.assertRaises(Exception) as context:
            self.client._make_request("test_endpoint")
        
        self.assertIn("Erro ao acessar API do ONS", str(context.exception))
    
    @patch.object(ONSClient, '_make_request')
    def test_search_datasets(self, mock_request):
        """Testa busca de datasets"""
        mock_request.return_value = {
            "success": True,
            "result": {
                "results": [
                    {"name": "dataset1", "title": "Dataset 1"},
                    {"name": "dataset2", "title": "Dataset 2"}
                ]
            }
        }
        
        results = self.client.search_datasets("carga")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], "dataset1")
    
    @patch.object(ONSClient, '_make_request')
    def test_get_dataset_info(self, mock_request):
        """Testa obtenção de informações de dataset"""
        mock_request.return_value = {
            "success": True,
            "result": {
                "id": "test-id",
                "name": "test-dataset",
                "title": "Test Dataset"
            }
        }
        
        info = self.client.get_dataset_info("test-id")
        
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "test-dataset")
        self.assertEqual(info["title"], "Test Dataset")


if __name__ == "__main__":
    unittest.main()
