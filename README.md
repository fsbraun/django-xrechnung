# django-xrechnung

A Django app for handling XRechnung (German electronic invoicing standard).

## Features

- Django models for XRechnung invoices and line items
- Admin interface for managing invoices
- REST API endpoints for programmatic access
- XML export functionality
- Configurable through pyproject.toml and Django settings
- Comprehensive test suite using pytest

## Installation

Install the package using pip:

```bash
pip install django-xrechnung
```

Or install in development mode:

```bash
pip install -e .[dev]
```

## Quick Start

1. Add `django_xrechnung` to your Django `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'django_xrechnung',
]
```

2. Include the URLs in your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... other patterns
    path('xrechnung/', include('django_xrechnung.urls')),
]
```

3. Run migrations:

```bash
python manage.py makemigrations django_xrechnung
python manage.py migrate
```

4. (Optional) Create a superuser to access the admin interface:

```bash
python manage.py createsuperuser
```

## Configuration

You can configure django-xrechnung through your `pyproject.toml` file:

```toml
[tool.django-xrechnung]
CURRENCY = "EUR"
DEFAULT_TAX_RATE = 19.00
PAGINATION_SIZE = 20
XML_VALIDATION = true
REQUIRE_TAX_ID = false
ALLOW_NEGATIVE_AMOUNTS = false
```

Or through Django settings:

```python
DJANGO_XRECHNUNG = {
    'CURRENCY': 'EUR',
    'DEFAULT_TAX_RATE': 19.00,
    'PAGINATION_SIZE': 20,
    'XML_VALIDATION': True,
    'REQUIRE_TAX_ID': False,
    'ALLOW_NEGATIVE_AMOUNTS': False,
}
```

## Usage

### Creating Invoices

```python
from django_xrechnung.models import XRechnungInvoice, XRechnungLineItem
from decimal import Decimal
from datetime import date

# Create an invoice
invoice = XRechnungInvoice.objects.create(
    invoice_number="INV-2024-001",
    invoice_date=date.today(),
    supplier_name="Your Company Ltd.",
    supplier_tax_id="DE123456789",
    buyer_name="Customer Inc.",
    buyer_tax_id="DE987654321",
    total_amount=Decimal("119.00"),
    tax_amount=Decimal("19.00"),
    net_amount=Decimal("100.00"),
    currency="EUR"
)

# Add line items
line_item = XRechnungLineItem.objects.create(
    invoice=invoice,
    position=1,
    description="Professional Services",
    quantity=Decimal("1.0"),
    unit_price=Decimal("100.00"),
    line_total=Decimal("100.00"),
    tax_rate=Decimal("19.00")
)
```

### Using the API

The app provides REST API endpoints:

- `GET /xrechnung/api/invoices/` - List all invoices
- `GET /xrechnung/api/invoices/{id}/` - Get invoice details
- `GET /xrechnung/api/invoices/{id}/xml/` - Export invoice as XML

### Admin Interface

Access the Django admin interface to manage invoices through a web interface.

## Development

### Setting up for Development

1. Clone the repository:

```bash
git clone https://github.com/fsbraun/django-xrechnung.git
cd django-xrechnung
```

2. Install development dependencies:

```bash
pip install -e .[dev]
```

3. Set up pre-commit hooks:

```bash
pre-commit install
```

4. Run tests:

```bash
pytest
```

4. Run tests with coverage:

```bash
pytest --cov=django_xrechnung
```

### Running Tests

The project uses pytest for testing. Tests are configured in `pyproject.toml`:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=django_xrechnung --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

### Code Quality

The project includes pre-commit hooks for code quality and consistency. Install and set up pre-commit:

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install the git hooks
pre-commit install

# Run hooks on all files (optional)
pre-commit run --all-files
```

The pre-commit configuration includes basic file validation hooks. For additional code formatting and linting, install the development tools:

```bash
# Install additional development tools
pip install black ruff isort mypy bandit

# Then uncomment the local hooks in .pre-commit-config.yaml for:
# - Code formatting with black
# - Linting with ruff
# - Import sorting with isort
# - Django-specific checks
# - Test execution
```

You can also run the tools manually:

```bash
# Format code with black
black .

# Lint with ruff
ruff check .

# Type checking with mypy
mypy django_xrechnung/

# Run pre-commit hooks manually on all files
pre-commit run --all-files
```

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

### 0.1.0 (2024-01-XX)

- Initial release
- Basic XRechnung invoice and line item models
- Django admin integration
- REST API endpoints
- XML export functionality
- Configurable through pyproject.toml
- Comprehensive test suite
