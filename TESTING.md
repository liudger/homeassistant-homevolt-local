# Testing

This project includes a comprehensive testing suite to ensure code quality and reliability.

## Test Structure

The tests are organized in the `tests/` directory with the following structure:

- `conftest.py` - Test fixtures and common utilities
- `test_const.py` - Tests for constants and configuration values
- `test_models.py` - Tests for data models and data classes
- `test_sensor.py` - Tests for sensor entities and functionality
- `test_config_flow.py` - Tests for configuration flow
- `test_coordinator.py` - Tests for data coordinator (partial implementation)

## Running Tests

### Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install pytest pytest-cov pytest-asyncio homeassistant
```

### Running All Tests

```bash
pytest tests/
```

### Running Specific Test Files

```bash
pytest tests/test_const.py
pytest tests/test_models.py
pytest tests/test_sensor.py
```

### Running with Coverage

```bash
pytest tests/ --cov=custom_components/homevolt_local --cov-report=term-missing
```

### Running with Verbose Output

```bash
pytest tests/ -v
```

## Test Coverage

Current test coverage focuses on:

- ✅ **Constants** (100% coverage) - All configuration constants and values
- ✅ **Data Models** (96% coverage) - Data classes and model validation
- ✅ **Sensor Platform** (26% coverage) - Basic sensor entity functionality
- ✅ **Config Flow** (Basic constants and structure validation)
- ⚠️ **Coordinator** (Partial) - Basic initialization and setup

## Testing in Development Container

The development container includes all testing dependencies and is configured to run tests properly:

1. Open the project in the dev container (VS Code or PyCharm)
2. Run tests using the integrated terminal:
   ```bash
   pytest tests/
   ```

The dev container is pre-configured with:
- pytest and pytest-cov for testing
- All Home Assistant dependencies
- Proper Python environment setup

## Test Configuration

Tests are configured using `pytest.ini`:

- Test discovery in `tests/` directory
- Coverage reporting with 80% minimum threshold
- HTML coverage reports generated in `htmlcov/`
- Proper async test handling with pytest-asyncio

## Writing New Tests

When adding new functionality:

1. Create corresponding test files in `tests/`
2. Follow the existing test patterns and naming conventions
3. Use the fixtures in `conftest.py` for common mock objects
4. Ensure tests are isolated and don't depend on external resources
5. Add both positive and negative test cases
6. Mock external dependencies (Home Assistant components, network calls, etc.)

## Mock Data

The tests use realistic mock data that matches the structure expected by the integration:

- Sample Homevolt device data
- Sample sensor configurations
- Mock Home Assistant coordinator objects
- Sample configuration entry data

## Continuous Integration

The testing setup is designed to work well with CI/CD pipelines and can be easily integrated with GitHub Actions or other CI systems.