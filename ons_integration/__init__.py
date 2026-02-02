"""
ONS Data Integration Module
Integração para obtenção de dados reais da ONS (Operador Nacional do Sistema Elétrico)
https://dados.ons.org.br/
"""

from .client import ONSClient
from .models import EnergyData, LoadData, GenerationData

__version__ = "0.1.0"
__all__ = ["ONSClient", "EnergyData", "LoadData", "GenerationData"]
