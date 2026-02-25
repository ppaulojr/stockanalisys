"""
Data fetcher module for Brazilian energy data including:
- Reservoir levels
- CCEE PLD prices
- Grid power consumption
"""
import requests
from datetime import datetime
import logging
from ons_integration import ONSClient
from ccee_client import CCEEClient

logger = logging.getLogger(__name__)

CACHE_TTL = 3600  # 1 hour in seconds

class EnergyDataFetcher:
    """Fetches Brazilian energy sector data"""
    
    def __init__(self):
        self.ons_url = "http://www.ons.org.br"
        self.ons_client = ONSClient()
        self.ccee_client = CCEEClient()
        # In-memory cache
        self._reservoir_cache = None
        self._reservoir_cache_time = None
        self._pld_cache = None
        self._pld_cache_time = None
        self._consumption_cache = None
        self._consumption_cache_time = None
        self._weather_cache = None
        self._weather_cache_time = None
        
    def get_reservoir_data(self, force=False):
        """
        Get current reservoir levels data from ONS
        
        Uses the direct S3 access method based on:
        https://github.com/ONSBR/DadosAbertos
        """
        if not force and self._reservoir_cache is not None:
            elapsed = (datetime.now() - self._reservoir_cache_time).total_seconds()
            if elapsed < CACHE_TTL:
                logger.info("Returning cached reservoir data (age: %.0fs)", elapsed)
                return self._reservoir_cache

        try:
            # Try to get real data directly from ONS S3 (preferred method)
            # Reference: https://github.com/ONSBR/DadosAbertos
            parsed_data = self.ons_client.get_reservoir_data_from_s3()
            
            if parsed_data:
                logger.info("Successfully retrieved reservoir data from ONS S3")
                parsed_data['data_source'] = 'ONS S3'
                parsed_data['note'] = 'Data retrieved directly from ONS S3 bucket'
                self._reservoir_cache = parsed_data
                self._reservoir_cache_time = datetime.now()
                return parsed_data
            
            # Fallback to CKAN API search
            logger.info("S3 method failed, trying CKAN API search...")
            datasets = self.ons_client.search_datasets("reservatorio")
            
            # Check if ONS API is accessible
            ons_accessible = len(datasets) > 0
            
            if ons_accessible:
                logger.info(f"Found {len(datasets)} reservoir datasets from ONS")
                # Parse actual reservoir data from ONS dataset resources
                parsed_data = self.ons_client.parse_reservoir_data(datasets)
            
            if parsed_data:
                # Successfully parsed real data from ONS
                logger.info("Successfully parsed reservoir data from ONS")
                parsed_data['data_source'] = 'ONS API'
                parsed_data['note'] = 'Data successfully retrieved and parsed from ONS'
                self._reservoir_cache = parsed_data
                self._reservoir_cache_time = datetime.now()
                return parsed_data
            elif ons_accessible:
                # ONS is accessible but parsing failed, use fallback with note
                logger.warning("ONS API accessible but data parsing failed, using fallback data")
                data_source = 'Fallback data'
                note = 'ONS API accessible but data format not recognized'
            else:
                # ONS API not accessible
                logger.warning("No datasets found from ONS, using fallback data")
                data_source = 'Fallback data'
                note = 'ONS API temporarily unavailable'
            
            # Return fallback data structure
            result = {
                'southeast': {
                    'level_percent': 65.4,
                    'capacity_mwmed': 208355,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'normal'
                },
                'south': {
                    'level_percent': 58.2,
                    'capacity_mwmed': 19768,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'normal'
                },
                'northeast': {
                    'level_percent': 42.8,
                    'capacity_mwmed': 56468,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'attention'
                },
                'north': {
                    'level_percent': 71.3,
                    'capacity_mwmed': 13489,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'normal'
                },
                'data_source': data_source,
                'note': note
            }
            self._reservoir_cache = result
            self._reservoir_cache_time = datetime.now()
            return result
        except Exception as e:
            logger.error(f"Error fetching reservoir data: {str(e)}")
            return {'error': str(e)}
    
    def get_pld_prices(self, force=False):
        """
        Get CCEE PLD (Preço de Liquidação das Diferenças) prices
        
        Fetches real PLD data from CCEE Dados Abertos portal.
        Falls back to cached/simulated data if CCEE API is unavailable.
        """
        if not force and self._pld_cache is not None:
            elapsed = (datetime.now() - self._pld_cache_time).total_seconds()
            if elapsed < CACHE_TTL:
                logger.info("Returning cached PLD prices (age: %.0fs)", elapsed)
                return self._pld_cache

        try:
            # Try to get real PLD data from CCEE Dados Abertos
            pld_data = self.ccee_client.get_pld_data()
            
            if pld_data:
                logger.info("Successfully retrieved PLD data from CCEE Dados Abertos")
                self._pld_cache = pld_data
                self._pld_cache_time = datetime.now()
                return pld_data
            
            # Fallback to simulated data if CCEE API is unavailable
            logger.warning("CCEE API unavailable, using fallback PLD data")
            result = {
                'southeast': {
                    'price': 145.32,
                    'submercado': 'SE/CO',
                    'currency': 'BRL/MWh',
                    'timestamp': datetime.now().isoformat()
                },
                'south': {
                    'price': 138.75,
                    'submercado': 'S',
                    'currency': 'BRL/MWh',
                    'timestamp': datetime.now().isoformat()
                },
                'northeast': {
                    'price': 152.18,
                    'submercado': 'NE',
                    'currency': 'BRL/MWh',
                    'timestamp': datetime.now().isoformat()
                },
                'north': {
                    'price': 148.90,
                    'submercado': 'N',
                    'currency': 'BRL/MWh',
                    'timestamp': datetime.now().isoformat()
                },
                'data_source': 'Fallback data',
                'note': 'CCEE API temporarily unavailable - using fallback data'
            }
            self._pld_cache = result
            self._pld_cache_time = datetime.now()
            return result
        except Exception as e:
            logger.error(f"Error fetching PLD prices: {str(e)}")
            return {'error': str(e)}
    
    def get_weather_data(self, force=False):
        """
        Get average monthly temperature and precipitation data for Brazil.

        Returns representative national averages based on historical climate data.
        """
        if not force and self._weather_cache is not None:
            elapsed = (datetime.now() - self._weather_cache_time).total_seconds()
            if elapsed < CACHE_TTL:
                logger.info("Returning cached weather data (age: %.0fs)", elapsed)
                return self._weather_cache

        try:
            months = [
                'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
            ]
            # National average temperature (°C) and precipitation (mm) for Brazil
            temperature = [27.1, 27.0, 26.8, 26.2, 25.1, 24.0,
                           23.8, 24.5, 25.2, 26.0, 26.7, 27.0]
            precipitation = [210, 180, 175, 120, 80, 55,
                              45, 50, 95, 150, 185, 205]

            result = {
                'months': months,
                'temperature': {
                    'values': temperature,
                    'unit': '°C',
                    'label': 'Average Temperature'
                },
                'precipitation': {
                    'values': precipitation,
                    'unit': 'mm',
                    'label': 'Average Precipitation'
                },
                'data_source': 'Historical climate averages',
                'note': 'National monthly averages based on historical Brazilian climate data'
            }
            self._weather_cache = result
            self._weather_cache_time = datetime.now()
            return result
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            return {'error': str(e)}

    def get_grid_consumption(self, force=False):
        """
        Get current power consumption in the Brazilian grid from ONS
        
        Uses the direct S3 access method based on:
        https://github.com/ONSBR/DadosAbertos
        """
        if not force and self._consumption_cache is not None:
            elapsed = (datetime.now() - self._consumption_cache_time).total_seconds()
            if elapsed < CACHE_TTL:
                logger.info("Returning cached consumption data (age: %.0fs)", elapsed)
                return self._consumption_cache

        try:
            # Try to get real data directly from ONS S3 (preferred method)
            # Reference: https://github.com/ONSBR/DadosAbertos
            parsed_data = self.ons_client.get_consumption_data_from_s3()
            
            if parsed_data:
                logger.info("Successfully retrieved consumption data from ONS S3")
                parsed_data['data_source'] = 'ONS S3'
                parsed_data['note'] = 'Data retrieved directly from ONS S3 bucket'
                self._consumption_cache = parsed_data
                self._consumption_cache_time = datetime.now()
                return parsed_data
            
            # Fallback to CKAN API search
            logger.info("S3 method failed, trying CKAN API search...")
            datasets = self.ons_client.search_datasets("carga")
            
            # Check if ONS API is accessible
            ons_accessible = len(datasets) > 0
            
            if ons_accessible:
                logger.info(f"Found {len(datasets)} load/consumption datasets from ONS")
                # Parse actual consumption data from ONS dataset resources
                parsed_data = self.ons_client.parse_consumption_data(datasets)
            
            if parsed_data:
                # Successfully parsed real data from ONS
                logger.info("Successfully parsed consumption data from ONS")
                parsed_data['data_source'] = 'ONS API'
                parsed_data['note'] = 'Data successfully retrieved and parsed from ONS'
                self._consumption_cache = parsed_data
                self._consumption_cache_time = datetime.now()
                return parsed_data
            elif ons_accessible:
                # ONS is accessible but parsing failed, use fallback with note
                logger.warning("ONS API accessible but data parsing failed, using fallback data")
                data_source = 'Fallback data'
                note = 'ONS API accessible but data format not recognized'
            else:
                # ONS API not accessible
                logger.warning("No datasets found from ONS, using fallback data")
                data_source = 'Fallback data'
                note = 'ONS API temporarily unavailable'
            
            # Return fallback data structure
            result = {
                'current_load_mw': 68542,
                'forecast_load_mw': 70125,
                'timestamp': datetime.now().isoformat(),
                'regions': {
                    'southeast': {'load_mw': 38245, 'percent': 55.8},
                    'south': {'load_mw': 9876, 'percent': 14.4},
                    'northeast': {'load_mw': 12543, 'percent': 18.3},
                    'north': {'load_mw': 7878, 'percent': 11.5}
                },
                'data_source': data_source,
                'note': note
            }
            self._consumption_cache = result
            self._consumption_cache_time = datetime.now()
            return result
        except Exception as e:
            logger.error(f"Error fetching grid consumption: {str(e)}")
            return {'error': str(e)}
