"""
CCEE API Client
Cliente para acessar dados abertos da CCEE (Câmara de Comercialização de Energia Elétrica)

Reference: https://dadosabertos.ccee.org.br/
The CCEE open data portal uses CKAN and provides free access to PLD prices and other
energy market data under Creative Commons Attribution 4.0 license.
"""

import json
import logging
import os
import requests
from datetime import datetime
from pathlib import Path
from requests.adapters import HTTPAdapter
from typing import List, Optional, Dict, Any
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class CCEEClient:
    """
    Cliente para integração com a API de dados abertos da CCEE

    A CCEE (Câmara de Comercialização de Energia Elétrica) disponibiliza dados
    do mercado de energia elétrico brasileiro no portal Dados Abertos.

    Datasets disponíveis incluem:
    - PLD_HORARIO: PLD horário por submercado
    - PLD_MEDIA_MENSAL: Média mensal do PLD por submercado
    """

    BASE_URL = "https://dadosabertos.ccee.org.br/api/3/action"

    # Known dataset IDs on CCEE Dados Abertos
    DATASETS = {
        "pld_horario": "pld_horario",
        "pld_media_mensal": "pld_media_mensal",
    }

    def __init__(self, timeout: int = 30, fixtures_path: Optional[str] = None, use_fixtures: Optional[bool] = None):
        """
        Inicializa o cliente CCEE

        Args:
            timeout: Tempo limite para requisições em segundos (padrão: 30)
            fixtures_path: Caminho para diretório de fixtures JSON para testes offline.
                          Se não fornecido, verifica a variável de ambiente CCEE_FIXTURES_PATH.
            use_fixtures: Se True, usa fixtures ao invés da API real.
                         Se não fornecido, verifica a variável de ambiente CCEE_USE_FIXTURES.
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://dadosabertos.ccee.org.br/",
        })

        # Configure retry logic for transient network errors
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Configure fixture loading for sandbox/offline testing
        if use_fixtures is not None:
            self.use_fixtures = use_fixtures
        else:
            self.use_fixtures = os.environ.get("CCEE_USE_FIXTURES", "").lower() == "true"
        self.fixtures_path = fixtures_path or os.environ.get("CCEE_FIXTURES_PATH", "")

    def _load_fixture(self, fixture_name: str) -> Optional[Dict[str, Any]]:
        """
        Carrega dados de fixture para testes offline

        Args:
            fixture_name: Nome do arquivo de fixture (sem extensão)

        Returns:
            Dados do fixture ou None se não encontrado
        """
        if not self.fixtures_path:
            return None

        fixtures_dir = Path(self.fixtures_path)
        if not fixtures_dir.exists():
            return None

        fixture_file = fixtures_dir / f"{fixture_name}.json"

        if fixture_file.exists():
            try:
                with open(fixture_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load fixture {fixture_file}: {e}")
                return None

        return None

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Faz uma requisição à API da CCEE

        Args:
            endpoint: Endpoint da API (e.g., 'package_show')
            params: Parâmetros da requisição

        Returns:
            Resposta da API em formato JSON

        Raises:
            Exception: Se houver erro na requisição
        """
        # Check if fixtures should be used
        if self.use_fixtures:
            # Build fixture name from endpoint and params
            fixture_name = f"ccee_{endpoint}"
            if params and 'id' in params:
                fixture_name += f"_{params['id']}"
            elif params and 'resource_id' in params:
                fixture_name += f"_{params['resource_id']}"

            fixture_data = self._load_fixture(fixture_name)
            if fixture_data is not None:
                return fixture_data
            raise Exception(f"Fixture not found: {fixture_name}")

        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Erro ao acessar API da CCEE: {str(e)}") from e

    def get_dataset_info(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações sobre um dataset da CCEE

        Args:
            dataset_id: ID do dataset (e.g., 'pld_horario')

        Returns:
            Informações do dataset ou None se não encontrado
        """
        try:
            result = self._make_request("package_show", {"id": dataset_id})
            if result.get("success"):
                return result.get("result")
            return None
        except Exception as e:
            logger.warning(f"Erro ao obter dataset CCEE {dataset_id}: {str(e)}")
            return None

    def get_resource_data(self, resource_id: str, limit: int = 100, sort: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Obtém dados de um recurso via CKAN datastore_search

        Args:
            resource_id: ID do recurso
            limit: Número máximo de registros (padrão: 100)
            sort: Campo para ordenação (e.g., 'dat_referencia desc')

        Returns:
            Lista de registros ou None se falhar
        """
        try:
            params = {
                "resource_id": resource_id,
                "limit": limit,
            }
            if sort:
                params["sort"] = sort

            result = self._make_request("datastore_search", params)
            if result.get("success"):
                return result.get("result", {}).get("records", [])
            return None
        except Exception as e:
            logger.warning(f"Erro ao obter dados do recurso CCEE {resource_id}: {str(e)}")
            return None

    def get_pld_data(self) -> Optional[Dict[str, Any]]:
        """
        Get current PLD prices from CCEE Dados Abertos

        Fetches the PLD hourly dataset, finds the most recent resource,
        and extracts the latest PLD values per submarket.

        Returns:
            Dictionary with PLD data by submarket or None if failed
        """
        try:
            # Step 1: Get the PLD hourly dataset info
            dataset = self.get_dataset_info("pld_horario")
            if not dataset:
                logger.warning("Could not fetch PLD dataset info from CCEE")
                return None

            # Step 2: Find the most recent resource (latest year)
            resources = dataset.get("resources", [])
            if not resources:
                logger.warning("No resources found in PLD dataset")
                return None

            # Sort resources by name to get the most recent year
            # Resources are typically named like "PLD_HORARIO_2025", "PLD_HORARIO_2024", etc.
            sorted_resources = sorted(
                resources,
                key=lambda r: r.get("name", ""),
                reverse=True
            )

            # Step 3: Try to get data from the most recent resource
            for resource in sorted_resources:
                resource_id = resource.get("id")
                if not resource_id:
                    continue

                # Fetch the latest records, sorted by date descending.
                # A full day has 96 records (24 hours × 4 submarkets);
                # use 200 to ensure we capture a complete day for averaging.
                records = self.get_resource_data(
                    resource_id,
                    limit=200,
                    sort="dat_referencia desc"
                )

                if records:
                    parsed = self._parse_pld_records(records)
                    if parsed:
                        return parsed

            logger.warning("No PLD data could be parsed from CCEE resources")
            return None

        except Exception as e:
            logger.error(f"Error fetching PLD data from CCEE: {str(e)}")
            return None

    def _parse_pld_records(self, records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Parse PLD records from CCEE CKAN datastore

        Expected fields (may vary by resource):
        - dat_referencia: Reference date
        - hora: Hour
        - id_subsistema: Submarket ID (SE, S, NE, N)
        - nom_subsistema: Submarket name
        - val_pld: PLD value in BRL/MWh

        Args:
            records: List of records from CCEE datastore

        Returns:
            Dictionary with PLD data by region or None
        """
        if not records:
            return None

        # Map CCEE submarket identifiers to our region keys
        submarket_mapping = {
            "SE": ("southeast", "SE/CO"),
            "SUDESTE": ("southeast", "SE/CO"),
            "SE/CO": ("southeast", "SE/CO"),
            "S": ("south", "S"),
            "SUL": ("south", "S"),
            "NE": ("northeast", "NE"),
            "NORDESTE": ("northeast", "NE"),
            "N": ("north", "N"),
            "NORTE": ("north", "N"),
        }

        # Group PLD values by (region, date) so we can compute daily averages
        region_date_values = {}  # {region_key: {date: [values], ...}}
        region_labels = {}  # {region_key: submercado_label}

        for record in records:
            # Get submarket identifier
            submarket_id = (
                record.get("id_subsistema") or
                record.get("nom_subsistema") or
                record.get("nom_submercado") or
                record.get("id_submercado") or
                ""
            ).upper().strip()

            mapping = submarket_mapping.get(submarket_id)
            if not mapping:
                continue

            region_key, submercado_label = mapping

            # Get PLD value
            pld_value = None
            for col in ["val_pld", "val_pld_medio", "val_pldmedio", "pld"]:
                if col in record and record[col]:
                    try:
                        val_str = str(record[col]).replace(",", ".")
                        pld_value = float(val_str)
                        break
                    except (ValueError, TypeError):
                        continue

            if pld_value is None:
                continue

            # Get date for comparison
            date_str = (
                record.get("dat_referencia") or
                record.get("din_instante") or
                record.get("data") or
                ""
            ).strip()

            # Collect all PLD values grouped by region and date
            if region_key not in region_date_values:
                region_date_values[region_key] = {}
            if date_str not in region_date_values[region_key]:
                region_date_values[region_key][date_str] = []
            region_date_values[region_key][date_str].append(pld_value)
            region_labels[region_key] = submercado_label

        if not region_date_values:
            return None

        # Build the result using the daily average for the most recent date per region
        result = {}
        for region_key, date_values in region_date_values.items():
            latest_date = max(date_values.keys())
            values = date_values[latest_date]
            avg_price = sum(values) / len(values)

            result[region_key] = {
                "price": round(avg_price, 2),
                "submercado": region_labels[region_key],
                "currency": "BRL/MWh",
                "timestamp": latest_date,
            }

        result["data_source"] = "CCEE Dados Abertos"
        result["note"] = "Daily average PLD data from CCEE (Câmara de Comercialização de Energia Elétrica)"

        return result
