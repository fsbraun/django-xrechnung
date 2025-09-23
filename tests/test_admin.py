import pytest
from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date
from django_xrechnung.models import XRechnungInvoice, XRechnungLineItem
from django_xrechnung.admin import XRechnungInvoiceAdmin, XRechnungLineItemAdmin


@pytest.mark.django_db
class TestXRechnungAdmin:
    """Test cases for XRechnung admin interface."""
    
    def test_invoice_admin_registration(self):
        """Test that admin classes are properly configured."""
        site = AdminSite()
        admin = XRechnungInvoiceAdmin(XRechnungInvoice, site)
        
        # Test list display
        expected_list_display = [
            "invoice_number",
            "invoice_date",
            "supplier_name",
            "buyer_name",
            "total_amount",
            "currency",
            "created_at",
        ]
        assert admin.list_display == expected_list_display
        
        # Test list filters
        expected_list_filter = [
            "invoice_date",
            "currency",
            "created_at",
        ]
        assert admin.list_filter == expected_list_filter
        
        # Test search fields
        expected_search_fields = [
            "invoice_number",
            "supplier_name",
            "buyer_name",
            "supplier_tax_id",
            "buyer_tax_id",
        ]
        assert admin.search_fields == expected_search_fields
    
    def test_line_item_admin_registration(self):
        """Test that line item admin is properly configured."""
        site = AdminSite()
        admin = XRechnungLineItemAdmin(XRechnungLineItem, site)
        
        # Test list display
        expected_list_display = [
            "invoice",
            "position",
            "description",
            "quantity",
            "unit_price",
            "line_total",
            "tax_rate",
        ]
        assert admin.list_display == expected_list_display
    
    def test_invoice_admin_readonly_fields_new(self):
        """Test readonly fields for new invoice."""
        site = AdminSite()
        admin = XRechnungInvoiceAdmin(XRechnungInvoice, site)
        
        # For new objects, only metadata fields should be readonly
        readonly_fields = admin.get_readonly_fields(None, None)
        expected_readonly = [
            "created_at",
            "updated_at",
            "net_amount",
        ]
        assert readonly_fields == expected_readonly
    
    def test_invoice_admin_readonly_fields_existing(self):
        """Test readonly fields for existing invoice."""
        invoice = XRechnungInvoice(
            invoice_number="INV-TEST-001",
            invoice_date=date.today(),
            supplier_name="Test Supplier",
            buyer_name="Test Buyer",
            total_amount=Decimal("100.00"),
        )
        
        site = AdminSite()
        admin = XRechnungInvoiceAdmin(XRechnungInvoice, site)
        
        # For existing objects, invoice_number should also be readonly
        readonly_fields = admin.get_readonly_fields(None, invoice)
        expected_readonly = [
            "created_at",
            "updated_at",
            "net_amount",
            "invoice_number",
        ]
        assert readonly_fields == expected_readonly


class TestAdminIntegration(TestCase):
    """Integration tests for admin interface."""
    
    def setUp(self):
        """Set up test data."""
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="adminpass123"
        )
        
        self.invoice = XRechnungInvoice.objects.create(
            invoice_number="INV-ADMIN-001",
            invoice_date=date.today(),
            supplier_name="Admin Test Supplier",
            buyer_name="Admin Test Buyer",
            total_amount=Decimal("119.00"),
            tax_amount=Decimal("19.00"),
            net_amount=Decimal("100.00"),
        )
    
    def test_admin_invoice_changelist(self):
        """Test admin changelist view for invoices."""
        self.client.login(username="admin", password="adminpass123")
        
        response = self.client.get("/admin/django_xrechnung/xrechnunginvoice/")
        assert response.status_code == 200
        assert "INV-ADMIN-001" in response.content.decode()
        assert "Admin Test Supplier" in response.content.decode()
    
    def test_admin_invoice_change(self):
        """Test admin change view for invoice."""
        self.client.login(username="admin", password="adminpass123")
        
        url = f"/admin/django_xrechnung/xrechnunginvoice/{self.invoice.pk}/change/"
        response = self.client.get(url)
        assert response.status_code == 200
        assert "INV-ADMIN-001" in response.content.decode()
    
    def test_admin_invoice_add(self):
        """Test admin add view for invoice."""
        self.client.login(username="admin", password="adminpass123")
        
        response = self.client.get("/admin/django_xrechnung/xrechnunginvoice/add/")
        assert response.status_code == 200
        assert "Add XRechnung Invoice" in response.content.decode()