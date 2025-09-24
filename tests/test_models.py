import pytest
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, timedelta
from django_xrechnung.models import XRechnungInvoice, XRechnungLineItem


@pytest.mark.django_db
class TestXRechnungInvoiceModel:
    """Test cases for XRechnungInvoice model."""

    def test_create_invoice(self):
        """Test creating a basic invoice."""
        invoice = XRechnungInvoice.objects.create(
            invoice_number="INV-2024-001",
            invoice_date=date.today(),
            supplier_name="Test Supplier Ltd.",
            supplier_tax_id="DE123456789",
            buyer_name="Test Buyer Inc.",
            buyer_tax_id="DE987654321",
            total_amount=Decimal("119.00"),
            tax_amount=Decimal("19.00"),
            net_amount=Decimal("100.00"),
            currency="EUR"
        )

        assert invoice.invoice_number == "INV-2024-001"
        assert invoice.supplier_name == "Test Supplier Ltd."
        assert invoice.total_amount == Decimal("119.00")
        assert str(invoice) == "Invoice INV-2024-001 - Test Supplier Ltd."

    def test_auto_calculate_net_amount(self):
        """Test that net amount is calculated automatically if not provided."""
        invoice = XRechnungInvoice.objects.create(
            invoice_number="INV-2024-002",
            invoice_date=date.today(),
            supplier_name="Test Supplier",
            buyer_name="Test Buyer",
            total_amount=Decimal("119.00"),
            tax_amount=Decimal("19.00"),
            # net_amount not provided - should be calculated
            currency="EUR"
        )

        assert invoice.net_amount == Decimal("100.00")

    def test_currency_validation(self):
        """Test that currency field validates 3-letter ISO codes."""
        with pytest.raises(ValidationError):
            invoice = XRechnungInvoice(
                invoice_number="INV-2024-003",
                invoice_date=date.today(),
                supplier_name="Test Supplier",
                buyer_name="Test Buyer",
                total_amount=Decimal("100.00"),
                currency="EURO"  # Invalid - too long
            )
            invoice.full_clean()

    def test_unique_invoice_number(self):
        """Test that invoice numbers must be unique."""
        XRechnungInvoice.objects.create(
            invoice_number="INV-2024-004",
            invoice_date=date.today(),
            supplier_name="Test Supplier 1",
            buyer_name="Test Buyer 1",
            total_amount=Decimal("100.00"),
        )

        # Try to create another invoice with same number
        with pytest.raises(Exception):  # Should raise IntegrityError
            XRechnungInvoice.objects.create(
                invoice_number="INV-2024-004",  # Duplicate
                invoice_date=date.today(),
                supplier_name="Test Supplier 2",
                buyer_name="Test Buyer 2",
                total_amount=Decimal("200.00"),
            )


@pytest.mark.django_db
class TestXRechnungLineItemModel:
    """Test cases for XRechnungLineItem model."""

    def test_create_line_item(self):
        """Test creating a line item."""
        invoice = XRechnungInvoice.objects.create(
            invoice_number="INV-2024-005",
            invoice_date=date.today(),
            supplier_name="Test Supplier",
            buyer_name="Test Buyer",
            total_amount=Decimal("119.00"),
        )

        line_item = XRechnungLineItem.objects.create(
            invoice=invoice,
            position=1,
            description="Test Product",
            quantity=Decimal("2.0"),
            unit_price=Decimal("50.00"),
            line_total=Decimal("100.00"),
            tax_rate=Decimal("19.00")
        )

        assert line_item.position == 1
        assert line_item.description == "Test Product"
        assert line_item.line_total == Decimal("100.00")
        assert str(line_item) == "Line 1: Test Product"

    def test_auto_calculate_line_total(self):
        """Test that line total is calculated automatically if not provided."""
        invoice = XRechnungInvoice.objects.create(
            invoice_number="INV-2024-006",
            invoice_date=date.today(),
            supplier_name="Test Supplier",
            buyer_name="Test Buyer",
            total_amount=Decimal("119.00"),
        )

        line_item = XRechnungLineItem.objects.create(
            invoice=invoice,
            position=1,
            description="Test Product",
            quantity=Decimal("3.0"),
            unit_price=Decimal("25.00"),
            # line_total not provided - should be calculated
            tax_rate=Decimal("19.00")
        )

        assert line_item.line_total == Decimal("75.00")

    def test_unique_position_per_invoice(self):
        """Test that position numbers must be unique within an invoice."""
        invoice = XRechnungInvoice.objects.create(
            invoice_number="INV-2024-007",
            invoice_date=date.today(),
            supplier_name="Test Supplier",
            buyer_name="Test Buyer",
            total_amount=Decimal("119.00"),
        )

        XRechnungLineItem.objects.create(
            invoice=invoice,
            position=1,
            description="Test Product 1",
            quantity=Decimal("1.0"),
            unit_price=Decimal("50.00"),
            line_total=Decimal("50.00"),
        )

        # Try to create another line item with same position
        with pytest.raises(Exception):  # Should raise IntegrityError
            XRechnungLineItem.objects.create(
                invoice=invoice,
                position=1,  # Duplicate position
                description="Test Product 2",
                quantity=Decimal("1.0"),
                unit_price=Decimal("60.00"),
                line_total=Decimal("60.00"),
            )


class TestXRechnungViews(TestCase):
    """Test cases for XRechnung views."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.invoice = XRechnungInvoice.objects.create(
            invoice_number="INV-TEST-001",
            invoice_date=date.today(),
            supplier_name="Test Supplier Ltd.",
            buyer_name="Test Buyer Inc.",
            total_amount=Decimal("119.00"),
            tax_amount=Decimal("19.00"),
            net_amount=Decimal("100.00"),
        )

        XRechnungLineItem.objects.create(
            invoice=self.invoice,
            position=1,
            description="Test Product",
            quantity=Decimal("1.0"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("100.00"),
            tax_rate=Decimal("19.00")
        )

    def test_invoice_list_view(self):
        """Test the invoice list view."""
        url = reverse("django_xrechnung:invoice_list")
        response = self.client.get(url)

        assert response.status_code == 200
        assert "INV-TEST-001" in response.content.decode()
        assert "Test Supplier Ltd." in response.content.decode()

    def test_invoice_detail_view(self):
        """Test the invoice detail view."""
        url = reverse("django_xrechnung:invoice_detail", kwargs={"pk": self.invoice.pk})
        response = self.client.get(url)

        assert response.status_code == 200
        assert "INV-TEST-001" in response.content.decode()
        assert "Test Product" in response.content.decode()

    def test_api_invoice_list_requires_auth(self):
        """Test that API endpoints require authentication."""
        url = reverse("django_xrechnung:api_invoice_list")
        response = self.client.get(url)

        # Should return 401 Unauthorized
        assert response.status_code == 401

    def test_api_invoice_list_authenticated(self):
        """Test API invoice list with authentication."""
        self.client.login(username="testuser", password="testpass123")

        url = reverse("django_xrechnung:api_invoice_list")
        response = self.client.get(url)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"

        data = response.json()
        assert "invoices" in data
        assert len(data["invoices"]) == 1
        assert data["invoices"][0]["invoice_number"] == "INV-TEST-001"

    def test_api_invoice_detail_authenticated(self):
        """Test API invoice detail with authentication."""
        self.client.login(username="testuser", password="testpass123")

        url = reverse("django_xrechnung:api_invoice_detail", kwargs={"pk": self.invoice.pk})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"

        data = response.json()
        assert data["invoice_number"] == "INV-TEST-001"
        assert data["supplier_name"] == "Test Supplier Ltd."
        assert len(data["line_items"]) == 1

    def test_xml_export(self):
        """Test XML export functionality."""
        url = reverse("django_xrechnung:api_invoice_xml", kwargs={"pk": self.invoice.pk})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response["Content-Type"] == "application/xml"
        assert "INV-TEST-001" in response.content.decode()

    def test_invoice_list_filtering(self):
        """Test filtering in invoice list view."""
        # Create another invoice with different supplier
        XRechnungInvoice.objects.create(
            invoice_number="INV-TEST-002",
            invoice_date=date.today(),
            supplier_name="Another Supplier",
            buyer_name="Test Buyer Inc.",
            total_amount=Decimal("200.00"),
        )

        # Test filtering by supplier
        url = reverse("django_xrechnung:invoice_list")
        response = self.client.get(url, {"supplier": "Test Supplier"})

        assert response.status_code == 200
        content = response.content.decode()
        assert "INV-TEST-001" in content
        assert "INV-TEST-002" not in content
