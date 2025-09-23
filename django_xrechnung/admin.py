from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import XRechnungInvoice, XRechnungLineItem


class XRechnungLineItemInline(admin.TabularInline):
    """Inline admin for line items within an invoice."""
    model = XRechnungLineItem
    extra = 1
    fields = ["position", "description", "quantity", "unit_price", "line_total", "tax_rate"]
    readonly_fields = ["line_total"]


@admin.register(XRechnungInvoice)
class XRechnungInvoiceAdmin(admin.ModelAdmin):
    """Admin interface for XRechnung invoices."""

    list_display = [
        "invoice_number",
        "invoice_date",
        "supplier_name",
        "buyer_name",
        "total_amount",
        "currency",
        "created_at",
    ]

    list_filter = [
        "invoice_date",
        "currency",
        "created_at",
    ]

    search_fields = [
        "invoice_number",
        "supplier_name",
        "buyer_name",
        "supplier_tax_id",
        "buyer_tax_id",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "net_amount",
    ]

    fieldsets = (
        (_("Invoice Information"), {
            "fields": (
                "invoice_number",
                "invoice_date",
                "due_date",
            )
        }),
        (_("Supplier Information"), {
            "fields": (
                "supplier_name",
                "supplier_tax_id",
            )
        }),
        (_("Buyer Information"), {
            "fields": (
                "buyer_name",
                "buyer_tax_id",
            )
        }),
        (_("Financial Information"), {
            "fields": (
                "total_amount",
                "tax_amount",
                "net_amount",
                "currency",
            )
        }),
        (_("XRechnung Data"), {
            "fields": (
                "xml_content",
            ),
            "classes": ("collapse",)
        }),
        (_("Metadata"), {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",)
        }),
    )

    inlines = [XRechnungLineItemInline]

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly when editing existing objects."""
        readonly = list(self.readonly_fields)
        if obj:  # Editing an existing object
            readonly.extend(["invoice_number"])
        return readonly


@admin.register(XRechnungLineItem)
class XRechnungLineItemAdmin(admin.ModelAdmin):
    """Admin interface for XRechnung line items."""

    list_display = [
        "invoice",
        "position",
        "description",
        "quantity",
        "unit_price",
        "line_total",
        "tax_rate",
    ]

    list_filter = [
        "tax_rate",
        "invoice__invoice_date",
    ]

    search_fields = [
        "description",
        "invoice__invoice_number",
        "invoice__supplier_name",
    ]

    readonly_fields = ["line_total"]

    ordering = ["invoice", "position"]
