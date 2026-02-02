# Stock Analysis Dashboard - AXIA & Brazilian Energy

Dashboard web para análise de ações AXIA e monitoramento do setor elétrico brasileiro / Web dashboard for AXIA stock analysis and Brazilian energy sector monitoring.

## Features / Funcionalidades

- 📊 **AXIA Stock Prices** - Real-time monitoring of AXIA3, AXIA6, and AXIA7 stock prices from B3 (Brazilian Stock Exchange)
- 💧 **Reservoir Levels** - Current water reservoir levels across Brazilian regions
- ⚡ **CCEE PLD Prices** - Settlement prices from the Brazilian Electric Energy Trading Chamber
- 🔌 **Grid Consumption** - Real-time power consumption data from the Brazilian grid

## Screenshots

![Dashboard Preview](https://github.com/user-attachments/assets/67c5513f-61d2-449b-9c39-10a4dd1a2f71)

## Installation / Instalação

### Requirements / Requisitos

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ppaulojr/stockanalisys.git
cd stockanalisys
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

For development with debug mode enabled:
```bash
FLASK_DEBUG=true python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage / Uso

The dashboard automatically loads and refreshes data every 60 seconds. You can also manually refresh individual sections using the "Refresh" buttons.

### Web Dashboard

The main dashboard provides a visual interface for monitoring AXIA stocks and Brazilian energy data.

### ONS Integration Module

The project includes a Python module for direct integration with ONS data API:

#### Example Usage

```python
from ons_integration import ONSClient

# Create client
client = ONSClient()

# List available datasets
datasets = client.list_datasets()
for dataset in datasets:
    print(f"Dataset: {dataset['name']}")
    print(f"Title: {dataset['title']}")

# Search specific datasets
datasets_carga = client.search_datasets("carga")
for dataset in datasets_carga:
    print(f"Load dataset: {dataset['title']}")

# Get dataset information
info = client.get_dataset_info("dataset-id")
if info:
    print(f"Description: {info['notes']}")
```

#### Run ONS Example

```bash
python example_ons.py
```

### API Endpoints

The application provides several REST API endpoints:

- `GET /api/axia/prices` - Get current AXIA stock prices
- `GET /api/axia/historical/<symbol>` - Get historical data for a specific AXIA symbol (AXIA3, AXIA6, or AXIA7)
- `GET /api/energy/reservoirs` - Get reservoir level data
- `GET /api/energy/pld` - Get CCEE PLD prices
- `GET /api/energy/consumption` - Get grid power consumption
- `GET /api/dashboard` - Get all dashboard data in a single request

### Example API Usage

```bash
# Get AXIA prices
curl http://localhost:5000/api/axia/prices

# Get reservoir data
curl http://localhost:5000/api/energy/reservoirs

# Get all dashboard data
curl http://localhost:5000/api/dashboard
```

## Data Sources / Fontes de Dados

- **Stock Data**: Yahoo Finance API via yfinance library
- **Energy Data**: Simulated data based on typical Brazilian grid operations
  - **Note**: Real implementation would require API access to:
    - ONS (Operador Nacional do Sistema Elétrico)
    - CCEE (Câmara de Comercialização de Energia Elétrica)

## Project Structure / Estrutura do Projeto

```
stockanalisys/
├── app.py                 # Flask application and API routes
├── axia_fetcher.py        # AXIA stock data fetcher
├── energy_fetcher.py      # Brazilian energy data fetcher
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Dashboard HTML template
└── README.md             # This file
```

## Deployment / Implantação

### Using Gunicorn (Production)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Contributing / Contribuindo

Contributions are welcome! Please feel free to submit a Pull Request.

## License / Licença

See LICENSE file for details.

## Author / Autor

Paulo Jr. (ppaulojr)

## Notes / Observações

This project uses simulated data for Brazilian energy sector information. For production use with real data, you would need to:

1. Register and obtain API credentials from ONS (Operador Nacional do Sistema Elétrico)
2. Register and obtain API credentials from CCEE (Câmara de Comercialização de Energia Elétrica)
3. Update the `energy_fetcher.py` module to use real API endpoints

The AXIA stock data is fetched in real-time from Yahoo Finance and reflects actual market data from B3 (Brazilian Stock Exchange).
