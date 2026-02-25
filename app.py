"""
Flask web application for AXIA stock and Brazilian energy dashboard
"""
from flask import Flask, render_template, jsonify, request
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
        force = request.args.get('force', 'false').lower() == 'true'
        prices = axia_fetcher.get_current_prices(force=force)
        return jsonify(prices)
    except Exception as e:
        logger.error(f"Error in /api/axia/prices: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/axia/historical/<symbol>')
def get_axia_historical(symbol):
    """API endpoint for AXIA historical data"""
    try:
        force = request.args.get('force', 'false').lower() == 'true'
        data = axia_fetcher.get_historical_data(symbol, period='1mo', force=force)
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
        force = request.args.get('force', 'false').lower() == 'true'
        data = energy_fetcher.get_reservoir_data(force=force)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/energy/reservoirs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/energy/pld')
def get_pld():
    """API endpoint for CCEE PLD prices"""
    try:
        force = request.args.get('force', 'false').lower() == 'true'
        data = energy_fetcher.get_pld_prices(force=force)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/energy/pld: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/energy/consumption')
def get_consumption():
    """API endpoint for grid power consumption"""
    try:
        force = request.args.get('force', 'false').lower() == 'true'
        data = energy_fetcher.get_grid_consumption(force=force)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/energy/consumption: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/energy/weather')
def get_weather():
    """API endpoint for average temperature and precipitation data"""
    try:
        force = request.args.get('force', 'false').lower() == 'true'
        data = energy_fetcher.get_weather_data(force=force)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/energy/weather: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard')
def get_dashboard_data():
    """Get all dashboard data in a single request"""
    try:
        force = request.args.get('force', 'false').lower() == 'true'
        data = {
            'axia_prices': axia_fetcher.get_current_prices(force=force),
            'reservoirs': energy_fetcher.get_reservoir_data(force=force),
            'pld_prices': energy_fetcher.get_pld_prices(force=force),
            'consumption': energy_fetcher.get_grid_consumption(force=force)
        }
        data['weather'] = energy_fetcher.get_weather_data(force=force)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in /api/dashboard: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
