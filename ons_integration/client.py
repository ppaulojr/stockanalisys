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
    
    def get_dataset_resource_data(self, resource_id: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """
        Obtém dados de um recurso específico de um dataset
        
        Args:
            resource_id: ID do recurso
            limit: Número máximo de registros a retornar (padrão: 100)
            
        Returns:
            Dados do recurso ou None se não encontrado
        """
        try:
            result = self._make_request("datastore_search", {
                "resource_id": resource_id,
                "limit": limit
            })
            
            if result.get("success"):
                return result.get("result", {}).get("records", [])
            
            return None
        except Exception as e:
            print(f"Aviso: Erro ao obter dados do recurso {resource_id}: {str(e)}")
            return None
    
    def parse_reservoir_data(self, datasets: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Parseia dados de reservatórios a partir de datasets do ONS
        
        Args:
            datasets: Lista de datasets retornados pela busca
            
        Returns:
            Dicionário com dados de reservatórios por região ou None se não encontrado
        """
        if not datasets:
            return None
        
        # Tentar encontrar recursos relevantes nos datasets
        for dataset in datasets:
            resources = dataset.get("resources", [])
            
            for resource in resources:
                # Procurar por recursos que contenham dados de reservatório
                resource_name = resource.get("name", "").lower()
                resource_format = resource.get("format", "").upper()
                
                # Priorizar recursos CSV ou JSON com dados recentes
                if resource_format in ["CSV", "JSON"] and any(
                    keyword in resource_name 
                    for keyword in ["reservatorio", "ear", "armazenamento"]
                ):
                    resource_id = resource.get("id")
                    if resource_id:
                        records = self.get_dataset_resource_data(resource_id, limit=10)
                        
                        if records and len(records) > 0:
                            # Parse o registro mais recente
                            return self._extract_reservoir_values(records)
        
        return None
    
    def _extract_reservoir_values(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extrai valores de reservatório de registros brutos do ONS
        
        Args:
            records: Lista de registros do dataset
            
        Returns:
            Dicionário estruturado com dados de reservatórios
        """
        # Pegar o registro mais recente (geralmente o primeiro)
        latest_record = records[0] if records else {}
        
        # Estrutura de retorno com dados por região
        result = {}
        
        # Mapear campos comuns do ONS para nossa estrutura
        # Os nomes de campos podem variar, então tentamos múltiplas possibilidades
        # Usar tuplas com prioridade: nomes mais específicos primeiro
        region_mappings = {
            "southeast": ["sudeste", "se_co", "seco", "se"],
            "south": ["sul", "s"],
            "northeast": ["nordeste", "ne"],
            "north": ["norte", "n"]
        }
        
        # Capacidades aproximadas por região (MWmed)
        capacities = {
            "southeast": 208355,
            "south": 19768,
            "northeast": 56468,
            "north": 13489
        }
        
        # Processar cada região, procurando o melhor match
        for region_key, region_names in region_mappings.items():
            best_match = None
            best_match_priority = -1
            
            for field_name in latest_record.keys():
                field_lower = field_name.lower().strip()
                
                # Verificar se o campo corresponde exatamente a algum nome da região
                for priority, region_name in enumerate(region_names):
                    if field_lower == region_name or field_lower.endswith("_" + region_name):
                        # Match exato ou sufixo, priorizar matches mais específicos
                        if priority > best_match_priority or best_match is None:
                            best_match = field_name
                            best_match_priority = priority
                            break
            
            # Se encontramos um match, extrair o valor
            if best_match:
                value = latest_record.get(best_match)
                
                if value is not None:
                    try:
                        level_percent = float(value)
                        
                        result[region_key] = {
                            "level_percent": level_percent,
                            "capacity_mwmed": capacities.get(region_key, 0),
                            "timestamp": latest_record.get("data", latest_record.get("timestamp", "")),
                            "status": "normal" if level_percent > 50 else "attention"
                        }
                    except (ValueError, TypeError):
                        continue
        
        return result if result else None
    
    def parse_consumption_data(self, datasets: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Parseia dados de consumo/carga a partir de datasets do ONS
        
        Args:
            datasets: Lista de datasets retornados pela busca
            
        Returns:
            Dicionário com dados de consumo ou None se não encontrado
        """
        if not datasets:
            return None
        
        # Tentar encontrar recursos relevantes nos datasets
        for dataset in datasets:
            resources = dataset.get("resources", [])
            
            for resource in resources:
                # Procurar por recursos que contenham dados de carga
                resource_name = resource.get("name", "").lower()
                resource_format = resource.get("format", "").upper()
                
                # Priorizar recursos CSV ou JSON com dados recentes
                if resource_format in ["CSV", "JSON"] and any(
                    keyword in resource_name 
                    for keyword in ["carga", "demanda", "consumo", "load"]
                ):
                    resource_id = resource.get("id")
                    if resource_id:
                        records = self.get_dataset_resource_data(resource_id, limit=10)
                        
                        if records and len(records) > 0:
                            # Parse o registro mais recente
                            return self._extract_consumption_values(records)
        
        return None
    
    def _extract_consumption_values(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extrai valores de consumo de registros brutos do ONS
        
        Args:
            records: Lista de registros do dataset
            
        Returns:
            Dicionário estruturado com dados de consumo
        """
        # Pegar o registro mais recente (geralmente o primeiro)
        latest_record = records[0] if records else {}
        
        result = {
            "current_load_mw": 0,
            "forecast_load_mw": 0,
            "timestamp": latest_record.get("data", latest_record.get("timestamp", "")),
            "regions": {}
        }
        
        # Mapear campos comuns do ONS
        # Usar lista ordenada por especificidade
        region_mappings = {
            "southeast": ["sudeste", "se_co", "seco", "se"],
            "south": ["sul", "s"],
            "northeast": ["nordeste", "ne"],
            "north": ["norte", "n"]
        }
        
        total_load = 0
        
        # Processar cada região, procurando o melhor match
        for region_key, region_names in region_mappings.items():
            best_match = None
            best_match_priority = -1
            
            for field_name in latest_record.keys():
                field_lower = field_name.lower().strip()
                
                # Verificar se o campo corresponde exatamente a algum nome da região
                for priority, region_name in enumerate(region_names):
                    if field_lower == region_name or field_lower.endswith("_" + region_name):
                        # Match exato ou sufixo, priorizar matches mais específicos
                        if priority > best_match_priority or best_match is None:
                            best_match = field_name
                            best_match_priority = priority
                            break
            
            # Se encontramos um match, extrair o valor
            if best_match:
                value = latest_record.get(best_match)
                
                if value is not None:
                    try:
                        load_mw = float(value)
                        total_load += load_mw
                        result["regions"][region_key] = {
                            "load_mw": load_mw,
                            "percent": 0  # Será calculado depois
                        }
                    except (ValueError, TypeError):
                        continue
        
        # Calcular percentuais
        if total_load > 0:
            for region_key in result["regions"]:
                load_mw = result["regions"][region_key]["load_mw"]
                result["regions"][region_key]["percent"] = round((load_mw / total_load) * 100, 1)
            
            result["current_load_mw"] = int(total_load)
            # Forecast é tipicamente 2-5% maior que o atual
            result["forecast_load_mw"] = int(total_load * 1.03)
        
        return result if result["regions"] else None
