from django.urls import path
from .views import (
    XRechnungInvoiceListView,
    XRechnungInvoiceDetailView,
    XRechnungInvoiceApiView,
)

app_name = "django_xrechnung"

urlpatterns = [
    # Web views
    path("", XRechnungInvoiceListView.as_view(), name="invoice_list"),
    path("invoice/<int:pk>/", XRechnungInvoiceDetailView.as_view(), name="invoice_detail"),
    
    # API endpoints
    path("api/invoices/", XRechnungInvoiceApiView.invoice_list_api, name="api_invoice_list"),
    path("api/invoices/<int:pk>/", XRechnungInvoiceApiView.invoice_detail_api, name="api_invoice_detail"),
    path("api/invoices/<int:pk>/xml/", XRechnungInvoiceApiView.invoice_xml_export, name="api_invoice_xml"),
]