"""
Flask web application for AXIA stock and Brazilian energy dashboard
"""
from flask import Flask, render_template, jsonify
import logging
from axia_fetcher import AxiaDataFetcher
from energy_fetcher import EnergyDataFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize data fetchers
axia_fetcher = AxiaDataFetcher()
energy_fetcher = EnergyDataFetcher()

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/api/axia/prices')
def get_axia_prices():
    """API endpoint for AXIA stock prices"""
    try:
        prices = axia_fetcher.get_current_prices()
        return jsonify(prices)
    except Exception as e:
        logger.error(f"Error in /api/axia/prices: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/axia/historical/<symbol>')
def get_axia_historical(symbol):
    """API endpoint for AXIA historical data"""
    try:
        data = axia_fetcher.get_historical_data(symbol, period='1mo')
        if data is None:
            return jsonify({'error': 'Symbol not found or no data available'}), 404
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/axia/historical/{symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/energy/reservoirs')
def get_reservoirs():
    """API endpoint for reservoir data"""
    try:
        data = energy_fetcher.get_reservoir_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/energy/reservoirs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/energy/pld')
def get_pld():
    """API endpoint for CCEE PLD prices"""
    try:
        data = energy_fetcher.get_pld_prices()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/energy/pld: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/energy/consumption')
def get_consumption():
    """API endpoint for grid power consumption"""
    try:
        data = energy_fetcher.get_grid_consumption()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/energy/consumption: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard')
def get_dashboard_data():
    """Get all dashboard data in a single request"""
    try:
        data = {
            'axia_prices': axia_fetcher.get_current_prices(),
            'reservoirs': energy_fetcher.get_reservoir_data(),
            'pld_prices': energy_fetcher.get_pld_prices(),
            'consumption': energy_fetcher.get_grid_consumption()
        }
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/dashboard: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
