# ONS API Test Fixtures

This directory contains fixture files that mirror the structure of data from ONS (Operador Nacional do Sistema Elétrico).

**Reference Implementation**: Based on the official ONS open data repository:
https://github.com/ONSBR/DadosAbertos

## Purpose

These fixtures serve multiple purposes:

1. **Sandbox/Offline Testing**: Allow running tests without network access to the real ONS data
2. **Development Reference**: Provide examples of expected data formats
3. **CI/CD Testing**: Enable automated testing in environments without external network access

## Data Sources

ONS provides data through two methods:

### 1. Direct S3 Access (Preferred)

Data is downloaded directly from ONS S3 buckets as CSV files:
- **Base URL**: `https://ons-dl-prod-opendata.s3.amazonaws.com/dataset/{dataset_name}/{filename}.csv`
- **Reference**: https://github.com/ONSBR/DadosAbertos

### 2. CKAN API (Metadata)

The CKAN API at `https://dados.ons.org.br/api/3/action/` provides dataset metadata.

## File Structure

### CSV Fixtures (S3 Data Format)

| Fixture File | Dataset | Description |
|--------------|---------|-------------|
| `ons_ear_subsistema.csv` | `ear_subsistema_di` | EAR (Stored Energy) by subsystem |
| `ons_carga_energia.csv` | `carga_energia` | Energy load/consumption |

### JSON Fixtures (CKAN API Format)

| Fixture File | Simulates Endpoint | Description |
|--------------|-------------------|-------------|
| `ons_package_list.json` | `/package_list` | List of all available dataset packages |
| `ons_package_search_reservatorio.json` | `/package_search?q=reservatorio` | Search results for reservoir datasets |
| `ons_package_search_carga.json` | `/package_search?q=carga` | Search results for load/consumption datasets |
| `ons_datastore_search_reservoir.json` | `/datastore_search?resource_id=...` | Reservoir data records |
| `ons_datastore_search_carga.json` | `/datastore_search?resource_id=...` | Load/consumption data records |

## Using Fixtures for Testing

### Option 1: Environment Variable Configuration

Set `ONS_USE_FIXTURES=true` to use local fixtures instead of real data:

```bash
export ONS_USE_FIXTURES=true
export ONS_FIXTURES_PATH=/path/to/tests/fixtures
python example_ons.py
```

### Option 2: Programmatic Configuration

```python
from ons_integration import ONSClient

client = ONSClient(fixtures_path="/path/to/fixtures", use_fixtures=True)

# Uses CSV fixtures for S3-based methods
ear_data = client.get_ear_subsistema()

# Uses JSON fixtures for CKAN API methods
datasets = client.search_datasets("reservatorio")
```

### Option 3: Unit Tests with Mocking

```python
import json
from unittest.mock import patch, Mock

# Load fixture
with open('tests/fixtures/ons_package_search_reservatorio.json') as f:
    mock_response = json.load(f)

# Patch the API call
with patch.object(client, '_make_request', return_value=mock_response):
    result = client.search_datasets("reservatorio")
```

## Data Format Reference

### EAR (Stored Energy) Data Fields - CSV Format

Based on: https://github.com/ONSBR/DadosAbertos

| Field | Type | Description |
|-------|------|-------------|
| `din_instante` | datetime | Timestamp of measurement |
| `id_subsistema` | string | Subsystem ID (SE, S, NE, N) |
| `nom_subsistema` | string | Subsystem name (SUDESTE, SUL, NORDESTE, NORTE) |
| `val_eararmazenavel_mwmes` | numeric | Maximum storable EAR (MWmonth) |
| `val_earverif_mwmes` | numeric | Verified EAR value (MWmonth) |
| `val_earverif_percentual` | numeric | EAR as percentage |

### Load/Consumption Data Fields - CSV Format

| Field | Type | Description |
|-------|------|-------------|
| `din_instante` | datetime | Timestamp of measurement |
| `id_subsistema` | string | Subsystem ID |
| `nom_subsistema` | string | Subsystem name |
| `val_cargaenergiamwmed` | numeric | Load value (MWmed) |

## Creating Custom Fixtures

### For CSV Fixtures (S3 data):

1. Download real data from ONS S3:
   ```
   https://ons-dl-prod-opendata.s3.amazonaws.com/dataset/{dataset_name}/{filename}.csv
   ```
2. Save as `ons_{dataset_key}.csv` in this directory
3. Use `;` as the delimiter (ONS standard)

### For JSON Fixtures (CKAN API):

1. Copy the structure from an existing fixture
2. Update the `result` section with appropriate test data
3. Follow the naming convention: `ons_{endpoint}_{optional_params}.json`

## Real ONS Data Documentation

- **Official Repository**: https://github.com/ONSBR/DadosAbertos
- **Data Portal**: https://dados.ons.org.br/
- **S3 Bucket**: https://ons-dl-prod-opendata.s3.amazonaws.com/dataset/
