"""
ONS API Client
Cliente para acessar dados da API do ONS (https://dados.ons.org.br/)
"""

import requests
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from .models import EnergyData, LoadData, GenerationData


class ONSClient:
    """
    Cliente para integração com a API de dados do ONS
    
    O ONS (Operador Nacional do Sistema Elétrico) disponibiliza dados
    sobre geração, carga e outras informações do sistema elétrico brasileiro.
    """
    
    BASE_URL = "https://dados.ons.org.br/api/3/action"
    
    def __init__(self, timeout: int = 30):
        """
        Inicializa o cliente ONS
        
        Args:
            timeout: Tempo limite para requisições em segundos (padrão: 30)
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "StockAnalysys-ONS-Integration/0.1.0"
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Faz uma requisição à API do ONS
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            
        Returns:
            Resposta da API em formato JSON
            
        Raises:
            requests.RequestException: Se houver erro na requisição
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Erro ao acessar API do ONS: {str(e)}") from e
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """
        Lista todos os datasets disponíveis no portal de dados do ONS
        
        Returns:
            Lista de datasets com seus metadados
        """
        try:
            result = self._make_request("package_list")
            
            if not result.get("success"):
                return []
            
            # Obter detalhes de cada dataset
            datasets = []
            package_ids = result.get("result", [])
            
            for package_id in package_ids[:10]:  # Limitar a 10 para não sobrecarregar
                try:
                    details = self.get_dataset_info(package_id)
                    if details:
                        datasets.append(details)
                except Exception:
                    continue
            
            return datasets
        except Exception as e:
            print(f"Aviso: Não foi possível listar datasets: {str(e)}")
            return []
    
    def get_dataset_info(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações sobre um dataset específico
        
        Args:
            dataset_id: ID do dataset
            
        Returns:
            Informações do dataset ou None se não encontrado
        """
        try:
            result = self._make_request("package_show", {"id": dataset_id})
            
            if result.get("success"):
                return result.get("result")
            
            return None
        except Exception as e:
            print(f"Aviso: Erro ao obter informações do dataset {dataset_id}: {str(e)}")
            return None
    
    def search_datasets(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca datasets por termo de pesquisa
        
        Args:
            query: Termo de busca
            
        Returns:
            Lista de datasets encontrados
        """
        try:
            result = self._make_request("package_search", {"q": query})
            
            if result.get("success"):
                return result.get("result", {}).get("results", [])
            
            return []
        except Exception as e:
            print(f"Aviso: Erro ao buscar datasets: {str(e)}")
            return []
    
    def get_energy_load(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[LoadData]:
        """
        Obtém dados de carga do sistema elétrico
        
        Args:
            start_date: Data inicial (padrão: 7 dias atrás)
            end_date: Data final (padrão: hoje)
            
        Returns:
            Lista de dados de carga
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now()
        
        # Buscar datasets relacionados à carga
        datasets = self.search_datasets("carga")
        
        load_data = []
        
        # Simular dados para demonstração (em produção, extrair dos datasets reais)
        # Nota: A implementação real depende da estrutura específica dos dados do ONS
        for dataset in datasets[:1]:  # Processar apenas o primeiro dataset
            try:
                # Extrair informações do dataset
                # Em produção, fazer parsing dos recursos (resources) do dataset
                pass
            except Exception as e:
                print(f"Aviso: Erro ao processar dataset de carga: {str(e)}")
        
        return load_data
    
    def get_generation_by_source(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[GenerationData]:
        """
        Obtém dados de geração por fonte de energia
        
        Args:
            start_date: Data inicial (padrão: 7 dias atrás)
            end_date: Data final (padrão: hoje)
            
        Returns:
            Lista de dados de geração por fonte
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now()
        
        # Buscar datasets relacionados à geração
        datasets = self.search_datasets("geracao")
        
        generation_data = []
        
        # Implementação similar ao get_energy_load
        # Em produção, processar os recursos dos datasets encontrados
        
        return generation_data
    
    def get_dataset_resource_data(self, resource_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Obtém dados de um recurso específico de um dataset
        
        Args:
            resource_id: ID do recurso
            
        Returns:
            Dados do recurso ou None se não encontrado
        """
        try:
            result = self._make_request("datastore_search", {
                "resource_id": resource_id,
                "limit": 100
            })
            
            if result.get("success"):
                return result.get("result", {}).get("records", [])
            
            return None
        except Exception as e:
            print(f"Aviso: Erro ao obter dados do recurso {resource_id}: {str(e)}")
            return None
