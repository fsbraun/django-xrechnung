from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class XRechnungInvoice(models.Model):
    """
    Model representing an XRechnung invoice.
    XRechnung is the German standard for electronic invoicing.
    """

    # Invoice identification
    invoice_number = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Unique invoice number")
    )

    # Dates
    invoice_date = models.DateField(
        help_text=_("Date when the invoice was issued")
    )

    due_date = models.DateField(
        blank=True,
        null=True,
        help_text=_("Payment due date")
    )

    # Supplier information
    supplier_name = models.CharField(
        max_length=200,
        help_text=_("Name of the supplier/seller")
    )

    supplier_tax_id = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Tax identification number of the supplier")
    )

    # Buyer information
    buyer_name = models.CharField(
        max_length=200,
        help_text=_("Name of the buyer/customer")
    )

    buyer_tax_id = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Tax identification number of the buyer")
    )

    # Financial information
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_("Total invoice amount including tax")
    )

    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Total tax amount")
    )

    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Net amount before tax")
    )

    # Currency
    currency = models.CharField(
        max_length=3,
        default="EUR",
        validators=[RegexValidator(r'^[A-Z]{3}$', _("Currency must be a 3-letter ISO code"))],
        help_text=_("Currency code (ISO 4217)")
    )

    # XRechnung specific fields
    xml_content = models.TextField(
        blank=True,
        help_text=_("XML content of the XRechnung")
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("XRechnung Invoice")
        verbose_name_plural = _("XRechnung Invoices")
        ordering = ["-invoice_date", "-created_at"]

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.supplier_name}"

    def save(self, *args, **kwargs):
        """
        Override save to calculate net amount if not provided.
        """
        if self.net_amount is None and self.total_amount and self.tax_amount:
            self.net_amount = self.total_amount - self.tax_amount
        super().save(*args, **kwargs)


class XRechnungLineItem(models.Model):
    """
    Model representing a line item in an XRechnung invoice.
    """

    invoice = models.ForeignKey(
        XRechnungInvoice,
        on_delete=models.CASCADE,
        related_name="line_items",
        help_text=_("Associated invoice")
    )

    position = models.PositiveIntegerField(
        help_text=_("Position number of this line item")
    )

    description = models.CharField(
        max_length=500,
        help_text=_("Description of the product or service")
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=1,
        help_text=_("Quantity of items")
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Price per unit")
    )

    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Total amount for this line item")
    )

    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=19.00,
        help_text=_("Tax rate as percentage (e.g., 19.00 for 19%)")
    )

    class Meta:
        verbose_name = _("XRechnung Line Item")
        verbose_name_plural = _("XRechnung Line Items")
        ordering = ["position"]
        unique_together = ["invoice", "position"]

    def __str__(self):
        return f"Line {self.position}: {self.description}"

    def save(self, *args, **kwargs):
        """
        Override save to calculate line total if not provided.
        """
        if self.line_total is None and self.quantity and self.unit_price:
            self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
