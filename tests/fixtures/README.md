# ONS API Test Fixtures

This directory contains sample JSON files that mirror the structure of responses from the ONS (Operador Nacional do Sistema Elétrico) API at `https://dados.ons.org.br/api/3/action/`.

## Purpose

These fixtures serve multiple purposes:

1. **Sandbox/Offline Testing**: Allow running tests without network access to the real ONS API
2. **Development Reference**: Provide examples of expected API response formats
3. **Mock Server Data**: Can be used to set up a local mock server for integration testing
4. **CI/CD Testing**: Enable automated testing in environments without external network access

## File Structure

### API Endpoint Mappings

| Fixture File | Simulates Endpoint | Description |
|--------------|-------------------|-------------|
| `ons_package_list.json` | `/package_list` | List of all available dataset packages |
| `ons_package_search_reservatorio.json` | `/package_search?q=reservatorio` | Search results for reservoir datasets |
| `ons_package_search_carga.json` | `/package_search?q=carga` | Search results for load/consumption datasets |
| `ons_datastore_search_reservoir.json` | `/datastore_search?resource_id=...` | Reservoir data records |
| `ons_datastore_search_carga.json` | `/datastore_search?resource_id=...` | Load/consumption data records |

## Using Fixtures for Testing

### Option 1: Unit Tests with Mocking

Use Python's `unittest.mock` to patch API calls:

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

### Option 2: Environment Variable Configuration

Set `ONS_USE_FIXTURES=true` to use local fixtures instead of the real API:

```bash
export ONS_USE_FIXTURES=true
export ONS_FIXTURES_PATH=/path/to/tests/fixtures
python example_ons.py
```

### Option 3: Mock Server

You can use these fixtures to set up a local mock server:

```bash
# Using Python's http.server with a simple router
python -m http.server 8080 --directory tests/fixtures

# Or use a more sophisticated tool like json-server
npx json-server --watch tests/fixtures/ons_package_list.json --port 8080
```

Then configure your client to use `http://localhost:8080` as the base URL.

## Data Format Reference

### Reservoir Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `data` | date | Date of measurement |
| `sudeste` | numeric | Southeast region reservoir level (%) |
| `sul` | numeric | South region reservoir level (%) |
| `nordeste` | numeric | Northeast region reservoir level (%) |
| `norte` | numeric | North region reservoir level (%) |

### Load/Consumption Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `data` | timestamp | Timestamp of measurement |
| `sudeste` | numeric | Southeast region load (MW) |
| `sul` | numeric | South region load (MW) |
| `nordeste` | numeric | Northeast region load (MW) |
| `norte` | numeric | North region load (MW) |

## Creating Custom Fixtures

To add new fixtures for additional endpoints:

1. Copy the structure from an existing fixture
2. Update the `help` URL to match the endpoint
3. Modify the `result` section with appropriate test data
4. Follow the naming convention: `ons_{endpoint}_{optional_params}.json`

## Real ONS API Documentation

For the most up-to-date information about the ONS API:
- Portal: https://dados.ons.org.br/
- API Documentation: https://dados.ons.org.br/api/3/action/help_show
