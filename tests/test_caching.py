"""
Tests for in-memory caching in AxiaDataFetcher and EnergyDataFetcher
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


class TestAxiaDataFetcherCache(unittest.TestCase):
    """Tests for AxiaDataFetcher caching logic"""

    def setUp(self):
        from axia_fetcher import AxiaDataFetcher
        self.fetcher = AxiaDataFetcher()
        self._sample_prices = {
            'AXIA3': {'symbol': 'AXIA3.SA', 'price': 10.0, 'timestamp': datetime.now().isoformat(), 'currency': 'BRL'}
        }

    def test_cache_is_empty_on_init(self):
        """Cache should be empty when the fetcher is first created"""
        self.assertIsNone(self.fetcher._prices_cache)
        self.assertIsNone(self.fetcher._prices_cache_time)

    def test_get_current_prices_stores_result_in_cache(self):
        """get_current_prices should populate the cache after a successful fetch"""
        with patch.object(self.fetcher, 'symbols', {'AXIA3': 'AXIA3.SA'}):
            import yfinance as yf
            import pandas as pd
            mock_ticker = MagicMock()
            mock_hist = pd.DataFrame({'Close': [10.0]})
            mock_ticker.history.return_value = mock_hist
            with patch('axia_fetcher.yf.Ticker', return_value=mock_ticker):
                result = self.fetcher.get_current_prices()

        self.assertIsNotNone(self.fetcher._prices_cache)
        self.assertIsNotNone(self.fetcher._prices_cache_time)
        self.assertEqual(result, self.fetcher._prices_cache)

    def test_get_current_prices_returns_cache_when_fresh(self):
        """get_current_prices should return cached data if it is less than CACHE_TTL old"""
        self.fetcher._prices_cache = self._sample_prices
        self.fetcher._prices_cache_time = datetime.now()

        with patch('axia_fetcher.yf.Ticker') as mock_ticker:
            result = self.fetcher.get_current_prices()
            mock_ticker.assert_not_called()

        self.assertEqual(result, self._sample_prices)

    def test_get_current_prices_bypasses_cache_when_force(self):
        """get_current_prices(force=True) should fetch fresh data even if cache is fresh"""
        self.fetcher._prices_cache = self._sample_prices
        self.fetcher._prices_cache_time = datetime.now()

        with patch.object(self.fetcher, 'symbols', {'AXIA3': 'AXIA3.SA'}):
            import pandas as pd
            mock_ticker = MagicMock()
            mock_hist = pd.DataFrame({'Close': [20.0]})
            mock_ticker.history.return_value = mock_hist
            with patch('axia_fetcher.yf.Ticker', return_value=mock_ticker):
                result = self.fetcher.get_current_prices(force=True)

        # The result should be fresh data, not the stale cache
        self.assertEqual(result['AXIA3']['price'], 20.0)

    def test_get_current_prices_fetches_fresh_data_when_cache_expired(self):
        """get_current_prices should fetch new data when the cache has expired"""
        self.fetcher._prices_cache = self._sample_prices
        self.fetcher._prices_cache_time = datetime.now() - timedelta(seconds=3601)

        with patch.object(self.fetcher, 'symbols', {'AXIA3': 'AXIA3.SA'}):
            import pandas as pd
            mock_ticker = MagicMock()
            mock_hist = pd.DataFrame({'Close': [30.0]})
            mock_ticker.history.return_value = mock_hist
            with patch('axia_fetcher.yf.Ticker', return_value=mock_ticker):
                result = self.fetcher.get_current_prices()

        self.assertEqual(result['AXIA3']['price'], 30.0)

    def test_historical_cache_is_empty_on_init(self):
        """Historical data cache should be empty when the fetcher is first created"""
        self.assertEqual(self.fetcher._historical_cache, {})
        self.assertEqual(self.fetcher._historical_cache_time, {})

    def test_get_historical_data_returns_cache_when_fresh(self):
        """get_historical_data should return cached data if it is less than CACHE_TTL old"""
        sample_data = [{'date': '2024-01-01', 'close': 10.0}]
        cache_key = 'AXIA3_1mo'
        self.fetcher._historical_cache[cache_key] = sample_data
        self.fetcher._historical_cache_time[cache_key] = datetime.now()

        with patch('axia_fetcher.yf.Ticker') as mock_ticker:
            result = self.fetcher.get_historical_data('AXIA3', period='1mo')
            mock_ticker.assert_not_called()

        self.assertEqual(result, sample_data)

    def test_get_historical_data_bypasses_cache_when_force(self):
        """get_historical_data(force=True) should bypass the cache"""
        sample_data = [{'date': '2024-01-01', 'close': 10.0}]
        cache_key = 'AXIA3_1mo'
        self.fetcher._historical_cache[cache_key] = sample_data
        self.fetcher._historical_cache_time[cache_key] = datetime.now()

        import pandas as pd
        mock_ticker = MagicMock()
        mock_hist = pd.DataFrame(
            {'Close': [50.0], 'Open': [49.0], 'High': [51.0], 'Low': [48.0], 'Volume': [1000]},
            index=pd.to_datetime(['2024-01-02'])
        )
        mock_ticker.history.return_value = mock_hist
        with patch('axia_fetcher.yf.Ticker', return_value=mock_ticker):
            result = self.fetcher.get_historical_data('AXIA3', period='1mo', force=True)

        self.assertEqual(result[0]['close'], 50.0)


class TestEnergyDataFetcherCache(unittest.TestCase):
    """Tests for EnergyDataFetcher caching logic"""

    def setUp(self):
        from energy_fetcher import EnergyDataFetcher
        with patch('energy_fetcher.ONSClient'), patch('energy_fetcher.CCEEClient'):
            self.fetcher = EnergyDataFetcher()
        self._sample_reservoir = {
            'southeast': {'level_percent': 65.4, 'status': 'normal'},
            'data_source': 'ONS S3'
        }
        self._sample_pld = {
            'southeast': {'price': 145.32, 'submercado': 'SE/CO', 'currency': 'BRL/MWh'},
            'data_source': 'CCEE Dados Abertos'
        }
        self._sample_consumption = {
            'current_load_mw': 68542,
            'regions': {},
            'data_source': 'ONS S3'
        }

    def test_cache_is_empty_on_init(self):
        """All caches should be empty when the fetcher is first created"""
        self.assertIsNone(self.fetcher._reservoir_cache)
        self.assertIsNone(self.fetcher._pld_cache)
        self.assertIsNone(self.fetcher._consumption_cache)

    def test_get_reservoir_data_returns_cache_when_fresh(self):
        """get_reservoir_data should return cached data if it is less than CACHE_TTL old"""
        self.fetcher._reservoir_cache = self._sample_reservoir
        self.fetcher._reservoir_cache_time = datetime.now()

        result = self.fetcher.get_reservoir_data()

        self.fetcher.ons_client.get_reservoir_data_from_s3.assert_not_called()
        self.assertEqual(result, self._sample_reservoir)

    def test_get_reservoir_data_bypasses_cache_when_force(self):
        """get_reservoir_data(force=True) should fetch fresh data"""
        self.fetcher._reservoir_cache = self._sample_reservoir
        self.fetcher._reservoir_cache_time = datetime.now()
        fresh = {'southeast': {'level_percent': 70.0, 'status': 'normal'}, 'data_source': 'ONS S3'}
        self.fetcher.ons_client.get_reservoir_data_from_s3.return_value = fresh

        result = self.fetcher.get_reservoir_data(force=True)

        self.fetcher.ons_client.get_reservoir_data_from_s3.assert_called_once()
        self.assertEqual(result['southeast']['level_percent'], 70.0)

    def test_get_reservoir_data_fetches_when_cache_expired(self):
        """get_reservoir_data should fetch new data when cache has expired"""
        self.fetcher._reservoir_cache = self._sample_reservoir
        self.fetcher._reservoir_cache_time = datetime.now() - timedelta(seconds=3601)
        fresh = {'southeast': {'level_percent': 80.0, 'status': 'normal'}, 'data_source': 'ONS S3'}
        self.fetcher.ons_client.get_reservoir_data_from_s3.return_value = fresh

        result = self.fetcher.get_reservoir_data()

        self.fetcher.ons_client.get_reservoir_data_from_s3.assert_called_once()
        self.assertEqual(result['southeast']['level_percent'], 80.0)

    def test_get_pld_prices_returns_cache_when_fresh(self):
        """get_pld_prices should return cached data if it is less than CACHE_TTL old"""
        self.fetcher._pld_cache = self._sample_pld
        self.fetcher._pld_cache_time = datetime.now()

        result = self.fetcher.get_pld_prices()

        self.fetcher.ccee_client.get_pld_data.assert_not_called()
        self.assertEqual(result, self._sample_pld)

    def test_get_pld_prices_bypasses_cache_when_force(self):
        """get_pld_prices(force=True) should fetch fresh data"""
        self.fetcher._pld_cache = self._sample_pld
        self.fetcher._pld_cache_time = datetime.now()
        fresh = {'southeast': {'price': 200.0, 'submercado': 'SE/CO', 'currency': 'BRL/MWh'}}
        self.fetcher.ccee_client.get_pld_data.return_value = fresh

        result = self.fetcher.get_pld_prices(force=True)

        self.fetcher.ccee_client.get_pld_data.assert_called_once()
        self.assertEqual(result['southeast']['price'], 200.0)

    def test_get_consumption_returns_cache_when_fresh(self):
        """get_grid_consumption should return cached data if it is less than CACHE_TTL old"""
        self.fetcher._consumption_cache = self._sample_consumption
        self.fetcher._consumption_cache_time = datetime.now()

        result = self.fetcher.get_grid_consumption()

        self.fetcher.ons_client.get_consumption_data_from_s3.assert_not_called()
        self.assertEqual(result, self._sample_consumption)

    def test_get_consumption_bypasses_cache_when_force(self):
        """get_grid_consumption(force=True) should fetch fresh data"""
        self.fetcher._consumption_cache = self._sample_consumption
        self.fetcher._consumption_cache_time = datetime.now()
        fresh = {'current_load_mw': 99999, 'regions': {}, 'data_source': 'ONS S3'}
        self.fetcher.ons_client.get_consumption_data_from_s3.return_value = fresh

        result = self.fetcher.get_grid_consumption(force=True)

        self.fetcher.ons_client.get_consumption_data_from_s3.assert_called_once()
        self.assertEqual(result['current_load_mw'], 99999)

    def test_get_reservoir_data_stores_result_in_cache(self):
        """get_reservoir_data should populate the cache after a successful fetch"""
        fresh = {'southeast': {'level_percent': 65.0, 'status': 'normal'}, 'data_source': 'ONS S3'}
        self.fetcher.ons_client.get_reservoir_data_from_s3.return_value = fresh

        result = self.fetcher.get_reservoir_data()

        self.assertIsNotNone(self.fetcher._reservoir_cache)
        self.assertIsNotNone(self.fetcher._reservoir_cache_time)
        self.assertEqual(result, self.fetcher._reservoir_cache)


if __name__ == "__main__":
    unittest.main()
