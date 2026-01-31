"""
Data fetcher module for AXIA stock prices from Brazilian stock exchange (B3)
"""
import yfinance as yf
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AxiaDataFetcher:
    """Fetches AXIA stock data from B3 (Brazilian stock exchange)"""
    
    def __init__(self):
        # AXIA stock symbols in B3 format
        self.symbols = {
            'AXIA3': 'AXIA3.SA',  # Common shares
            'AXIA6': 'AXIA6.SA',  # Preferred shares class A
            'AXIA7': 'AXIA7.SA',  # Preferred shares class B
        }
    
    def get_current_prices(self):
        """Get current prices for all AXIA stock classes"""
        prices = {}
        
        for name, symbol in self.symbols.items():
            try:
                ticker = yf.Ticker(symbol)
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
        
        return prices
    
    def get_historical_data(self, symbol_name, period='1mo'):
        """Get historical data for a specific AXIA symbol"""
        try:
            if symbol_name not in self.symbols:
                return None
            
            symbol = self.symbols[symbol_name]
            ticker = yf.Ticker(symbol)
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
            
            return data
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol_name}: {str(e)}")
            return None
