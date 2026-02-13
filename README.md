# Stock Analysis Dashboard - AXIA & Brazilian Energy

Dashboard web para análise de ações AXIA e monitoramento do setor elétrico brasileiro / Web dashboard for AXIA stock analysis and Brazilian energy sector monitoring.

## Features / Funcionalidades

- 📊 **AXIA Stock Prices** - Real-time monitoring of AXIA3, AXIA6, and AXIA7 stock prices from B3 (Brazilian Stock Exchange)
- 💧 **Reservoir Levels** - Current water reservoir levels across Brazilian regions
- ⚡ **CCEE PLD Prices** - Settlement prices from the Brazilian Electric Energy Trading Chamber
- 🔌 **Grid Consumption** - Real-time power consumption data from the Brazilian grid

## Screenshots

![Dashboard Preview](https://github.com/user-attachments/assets/d48ce7c3-8fd6-4bf6-aedd-6bd57d41e1e9)

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
- **Energy Data**: Real data from ONS (Operador Nacional do Sistema Elétrico)
  - **Note**: ONS provides free public API access at https://dados.ons.org.br/
  - **Note**: CCEE data is simulated and would require API credentials for real implementation

## Testing in Sandbox/Offline Environments

The ONS client supports fixture-based testing for environments without network access to the real ONS API (e.g., CI/CD pipelines, sandbox environments, or offline development).

### Enabling Fixture Mode

Set the following environment variables:

```bash
# Enable fixture loading instead of real API calls
export ONS_USE_FIXTURES=true

# Path to the directory containing fixture JSON files
export ONS_FIXTURES_PATH=/path/to/tests/fixtures
```

Or configure programmatically:

```python
from ons_integration import ONSClient

# Use fixtures from a specific directory
client = ONSClient(fixtures_path="/path/to/tests/fixtures")
client.use_fixtures = True

# Now all API calls will use local fixture files
datasets = client.search_datasets("reservatorio")
```

### Available Fixtures

The `tests/fixtures/` directory contains sample ONS API responses:

| Fixture File | Simulates |
|--------------|-----------|
| `ons_package_list.json` | List of all datasets |
| `ons_package_search_reservatorio.json` | Reservoir dataset search |
| `ons_package_search_carga.json` | Load/consumption dataset search |
| `ons_datastore_search_reservoir.json` | Reservoir data records |
| `ons_datastore_search_carga.json` | Load data records |

See `tests/fixtures/README.md` for detailed documentation on creating custom fixtures.

## Project Structure / Estrutura do Projeto

```
stockanalisys/
├── app.py                   # Flask application and API routes
├── axia_fetcher.py          # AXIA stock data fetcher
├── energy_fetcher.py        # Brazilian energy data fetcher
├── example_ons.py           # Example script for ONS integration
├── requirements.txt         # Python dependencies
├── ons_integration/         # ONS API integration module
│   ├── __init__.py
│   ├── client.py            # ONS API client with fixture support
│   └── models.py            # Data models
├── tests/
│   ├── fixtures/            # Sample ONS API responses for offline testing
│   │   ├── README.md        # Fixture documentation
│   │   └── *.json           # JSON fixture files
│   ├── test_client.py       # Client tests
│   ├── test_fixtures.py     # Fixture loading tests
│   ├── test_models.py       # Model tests
│   └── test_ons_parsing.py  # Parsing tests
├── templates/
│   └── index.html           # Dashboard HTML template
└── README.md                # This file
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

Pedro Paulo Oliveira Jr. (ppaulojr)

## Notes / Observações

This project uses real data from ONS (Operador Nacional do Sistema Elétrico) which provides free public API access at https://dados.ons.org.br/. 

CCEE (Câmara de Comercialização de Energia Elétrica) data is currently simulated. For production use with real CCEE data, you would need to register and obtain API credentials.

The AXIA stock data is fetched in real-time from Yahoo Finance and reflects actual market data from B3 (Brazilian Stock Exchange).
