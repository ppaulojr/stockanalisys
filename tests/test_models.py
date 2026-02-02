"""
Testes para os modelos de dados do ONS
"""

import unittest
from datetime import datetime
from ons_integration.models import EnergyData, LoadData, GenerationData


class TestEnergyData(unittest.TestCase):
    """Testes para o modelo EnergyData"""
    
    def test_from_dict(self):
        """Testa criação de EnergyData a partir de dicionário"""
        data = {
            "timestamp": "2024-01-15T10:00:00Z",
            "value": 1500.5,
            "unit": "MW",
            "source": "Hidro",
            "region": "SE"
        }
        
        energy = EnergyData.from_dict(data)
        
        self.assertIsInstance(energy.timestamp, datetime)
        self.assertEqual(energy.value, 1500.5)
        self.assertEqual(energy.unit, "MW")
        self.assertEqual(energy.source, "Hidro")
        self.assertEqual(energy.region, "SE")
    
    def test_from_dict_minimal(self):
        """Testa criação com dados mínimos"""
        data = {
            "timestamp": datetime.now(),
            "value": 100
        }
        
        energy = EnergyData.from_dict(data)
        
        self.assertEqual(energy.value, 100)
        self.assertEqual(energy.unit, "MW")
        self.assertIsNone(energy.source)
        self.assertIsNone(energy.region)


class TestLoadData(unittest.TestCase):
    """Testes para o modelo LoadData"""
    
    def test_from_dict(self):
        """Testa criação de LoadData a partir de dicionário"""
        data = {
            "timestamp": "2024-01-15T10:00:00Z",
            "load_mw": 75000.0,
            "region": "SIN",
            "verified": True
        }
        
        load = LoadData.from_dict(data)
        
        self.assertIsInstance(load.timestamp, datetime)
        self.assertEqual(load.load_mw, 75000.0)
        self.assertEqual(load.region, "SIN")
        self.assertTrue(load.verified)
    
    def test_from_dict_defaults(self):
        """Testa valores padrão"""
        data = {
            "timestamp": datetime.now(),
            "load_mw": 50000
        }
        
        load = LoadData.from_dict(data)
        
        self.assertEqual(load.region, "SIN")
        self.assertFalse(load.verified)


class TestGenerationData(unittest.TestCase):
    """Testes para o modelo GenerationData"""
    
    def test_from_dict(self):
        """Testa criação de GenerationData a partir de dicionário"""
        data = {
            "timestamp": "2024-01-15T10:00:00Z",
            "source_type": "eolica",
            "generation_mw": 12500.0,
            "region": "NE"
        }
        
        gen = GenerationData.from_dict(data)
        
        self.assertIsInstance(gen.timestamp, datetime)
        self.assertEqual(gen.source_type, "eolica")
        self.assertEqual(gen.generation_mw, 12500.0)
        self.assertEqual(gen.region, "NE")
    
    def test_from_dict_defaults(self):
        """Testa valores padrão"""
        data = {
            "timestamp": datetime.now(),
            "generation_mw": 1000
        }
        
        gen = GenerationData.from_dict(data)
        
        self.assertEqual(gen.source_type, "")
        self.assertEqual(gen.region, "SIN")


if __name__ == "__main__":
    unittest.main()
