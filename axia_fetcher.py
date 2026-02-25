"""
Data fetcher module for AXIA stock prices from Brazilian stock exchange (B3)
"""
import yfinance as yf
import requests
import certifi
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

CACHE_TTL = 3600  # 1 hour in seconds

class AxiaDataFetcher:
    """Fetches AXIA stock data from B3 (Brazilian stock exchange)"""
    
    def __init__(self):
        # AXIA stock symbols in B3 format
        self.symbols = {
            'AXIA3': 'AXIA3.SA',  # Common shares
            'AXIA6': 'AXIA6.SA',  # Preferred shares class A
            'AXIA7': 'AXIA7.SA',  # Preferred shares class B
        }
        # Create a session with proper SSL certificate verification
        self.session = requests.Session()
        self.session.verify = certifi.where()
        # In-memory cache
        self._prices_cache = None
        self._prices_cache_time = None
        self._historical_cache = {}
        self._historical_cache_time = {}

    def get_current_prices(self, force=False):
        """Get current prices for all AXIA stock classes"""
        if not force and self._prices_cache is not None:
            elapsed = (datetime.now() - self._prices_cache_time).total_seconds()
            if elapsed < CACHE_TTL:
                logger.info("Returning cached AXIA prices (age: %.0fs)", elapsed)
                return self._prices_cache

        prices = {}
        
        for name, symbol in self.symbols.items():
            try:
                ticker = yf.Ticker(symbol, session=self.session)
                hist = ticker.history(period='1d')
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prices[name] = {
                        'symbol': symbol,
                        'price': round(float(current_price), 2),
                        'timestamp': datetime.now().isoformat(),
                        'currency': 'BRL'
                    }
                else:
                    prices[name] = {
                        'symbol': symbol,
                        'price': None,
                        'timestamp': datetime.now().isoformat(),
                        'currency': 'BRL',
                        'error': 'No data available'
                    }
            except Exception as e:
                logger.error(f"Error fetching {name}: {str(e)}")
                prices[name] = {
                    'symbol': symbol,
                    'price': None,
                    'timestamp': datetime.now().isoformat(),
                    'currency': 'BRL',
                    'error': str(e)
                }
        
        self._prices_cache = prices
        self._prices_cache_time = datetime.now()
        return prices
    
    def get_historical_data(self, symbol_name, period='1mo', force=False):
        """Get historical data for a specific AXIA symbol"""
        cache_key = f"{symbol_name}_{period}"
        if not force and cache_key in self._historical_cache:
            elapsed = (datetime.now() - self._historical_cache_time[cache_key]).total_seconds()
            if elapsed < CACHE_TTL:
                logger.info("Returning cached historical data for %s (age: %.0fs)", symbol_name, elapsed)
                return self._historical_cache[cache_key]

        try:
            if symbol_name not in self.symbols:
                return None
            
            symbol = self.symbols[symbol_name]
            ticker = yf.Ticker(symbol, session=self.session)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            data = []
            for date, row in hist.iterrows():
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'close': round(float(row['Close']), 2),
                    'open': round(float(row['Open']), 2),
                    'high': round(float(row['High']), 2),
                    'low': round(float(row['Low']), 2),
                    'volume': int(row['Volume'])
                })
            
            self._historical_cache[cache_key] = data
            self._historical_cache_time[cache_key] = datetime.now()
            return data
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol_name}: {str(e)}")
            return None
