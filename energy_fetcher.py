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

logger = logging.getLogger(__name__)

class EnergyDataFetcher:
    """Fetches Brazilian energy sector data"""
    
    def __init__(self):
        self.ons_url = "http://www.ons.org.br"
        self.ons_client = ONSClient()
        
    def get_reservoir_data(self):
        """
        Get current reservoir levels data from ONS
        
        Uses the direct S3 access method based on:
        https://github.com/ONSBR/DadosAbertos
        """
        try:
            # Try to get real data directly from ONS S3 (preferred method)
            # Reference: https://github.com/ONSBR/DadosAbertos
            parsed_data = self.ons_client.get_reservoir_data_from_s3()
            
            if parsed_data:
                logger.info("Successfully retrieved reservoir data from ONS S3")
                parsed_data['data_source'] = 'ONS S3'
                parsed_data['note'] = 'Data retrieved directly from ONS S3 bucket'
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
            return {
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
        except Exception as e:
            logger.error(f"Error fetching reservoir data: {str(e)}")
            return {'error': str(e)}
    
    def get_pld_prices(self):
        """
        Get CCEE PLD (Preço de Liquidação das Diferenças) prices
        Note: This is simulated data as real API requires CCEE authentication
        """
        try:
            # In a real implementation, this would fetch from CCEE API
            # PLD prices are in BRL/MWh
            return {
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
                'note': 'Simulated data - Real implementation requires CCEE API access'
            }
        except Exception as e:
            logger.error(f"Error fetching PLD prices: {str(e)}")
            return {'error': str(e)}
    
    def get_grid_consumption(self):
        """
        Get current power consumption in the Brazilian grid from ONS
        
        Uses the direct S3 access method based on:
        https://github.com/ONSBR/DadosAbertos
        """
        try:
            # Try to get real data directly from ONS S3 (preferred method)
            # Reference: https://github.com/ONSBR/DadosAbertos
            parsed_data = self.ons_client.get_consumption_data_from_s3()
            
            if parsed_data:
                logger.info("Successfully retrieved consumption data from ONS S3")
                parsed_data['data_source'] = 'ONS S3'
                parsed_data['note'] = 'Data retrieved directly from ONS S3 bucket'
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
            return {
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
        except Exception as e:
            logger.error(f"Error fetching grid consumption: {str(e)}")
            return {'error': str(e)}
