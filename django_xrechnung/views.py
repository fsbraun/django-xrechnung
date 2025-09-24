from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import XRechnungInvoice, XRechnungLineItem
import json


class XRechnungInvoiceListView(ListView):
    """List view for XRechnung invoices."""
    model = XRechnungInvoice
    template_name = "django_xrechnung/invoice_list.html"
    context_object_name = "invoices"
    paginate_by = 20

    def get_queryset(self):
        """Filter invoices based on query parameters."""
        queryset = super().get_queryset()

        # Filter by supplier name
        supplier = self.request.GET.get("supplier")
        if supplier:
            queryset = queryset.filter(supplier_name__icontains=supplier)

        # Filter by date range
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        if start_date:
            queryset = queryset.filter(invoice_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(invoice_date__lte=end_date)

        return queryset


class XRechnungInvoiceDetailView(DetailView):
    """Detail view for a single XRechnung invoice."""
    model = XRechnungInvoice
    template_name = "django_xrechnung/invoice_detail.html"
    context_object_name = "invoice"

    def get_context_data(self, **kwargs):
        """Add line items to the context."""
        context = super().get_context_data(**kwargs)
        context["line_items"] = self.object.line_items.all()
        return context


@method_decorator(login_required, name="dispatch")
class XRechnungInvoiceApiView(DetailView):
    """API views for XRechnung invoices."""
    model = XRechnungInvoice

    @staticmethod
    @require_http_methods(["GET"])
    def invoice_list_api(request):
        """Return JSON list of invoices."""
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        invoices = XRechnungInvoice.objects.all()

        # Apply filters
        supplier = request.GET.get("supplier")
        if supplier:
            invoices = invoices.filter(supplier_name__icontains=supplier)

        data = []
        for invoice in invoices:
            data.append({
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "invoice_date": invoice.invoice_date.isoformat(),
                "supplier_name": invoice.supplier_name,
                "buyer_name": invoice.buyer_name,
                "total_amount": str(invoice.total_amount),
                "currency": invoice.currency,
            })

        return JsonResponse({"invoices": data})

    @staticmethod
    @require_http_methods(["GET"])
    def invoice_detail_api(request, pk):
        """Return JSON detail of a single invoice."""
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        invoice = get_object_or_404(XRechnungInvoice, pk=pk)

        data = {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date.isoformat(),
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "supplier_name": invoice.supplier_name,
            "supplier_tax_id": invoice.supplier_tax_id,
            "buyer_name": invoice.buyer_name,
            "buyer_tax_id": invoice.buyer_tax_id,
            "total_amount": str(invoice.total_amount),
            "tax_amount": str(invoice.tax_amount),
            "net_amount": str(invoice.net_amount),
            "currency": invoice.currency,
            "line_items": [
                {
                    "position": item.position,
                    "description": item.description,
                    "quantity": str(item.quantity),
                    "unit_price": str(item.unit_price),
                    "line_total": str(item.line_total),
                    "tax_rate": str(item.tax_rate),
                }
                for item in invoice.line_items.all()
            ],
        }

        return JsonResponse(data)

    @staticmethod
    @csrf_exempt
    @require_http_methods(["GET"])
    def invoice_xml_export(request, pk):
        """Export invoice as XML (basic implementation)."""
        invoice = get_object_or_404(XRechnungInvoice, pk=pk)

        if invoice.xml_content:
            return HttpResponse(
                invoice.xml_content,
                content_type="application/xml",
                headers={
                    "Content-Disposition": f'attachment; filename="invoice_{invoice.invoice_number}.xml"'
                },
            )
        else:
            # Generate basic XML if no content stored
            xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice>
    <InvoiceNumber>{invoice.invoice_number}</InvoiceNumber>
    <InvoiceDate>{invoice.invoice_date}</InvoiceDate>
    <Supplier>
        <Name>{invoice.supplier_name}</Name>
        <TaxID>{invoice.supplier_tax_id}</TaxID>
    </Supplier>
    <Buyer>
        <Name>{invoice.buyer_name}</Name>
        <TaxID>{invoice.buyer_tax_id}</TaxID>
    </Buyer>
    <TotalAmount currency="{invoice.currency}">{invoice.total_amount}</TotalAmount>
</Invoice>"""

            return HttpResponse(
                xml_content,
                content_type="application/xml",
                headers={
                    "Content-Disposition": f'attachment; filename="invoice_{invoice.invoice_number}.xml"'
                },
            )
