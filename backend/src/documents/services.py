"""
PDF generation service using WeasyPrint.
"""
import os
from pathlib import Path
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from src.billing.models import Invoice


class PDFGenerator:
    """Service for generating PDF documents."""
    
    def __init__(self):
        self.font_config = FontConfiguration()
        self.base_css = self._get_base_css()
    
    def _get_base_css(self):
        """Get base CSS styles for PDF."""
        return CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
                @top-center {
                    content: "Invoice";
                    font-size: 10pt;
                    color: #666;
                }
                @bottom-center {
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 10pt;
                    color: #666;
                }
            }
            
            body {
                font-family: Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.4;
                color: #333;
            }
            
            .header {
                text-align: center;
                margin-bottom: 2cm;
                border-bottom: 2px solid #333;
                padding-bottom: 1cm;
            }
            
            .company-info {
                text-align: left;
                margin-bottom: 1cm;
            }
            
            .invoice-details {
                display: flex;
                justify-content: space-between;
                margin-bottom: 2cm;
            }
            
            .invoice-info {
                text-align: right;
            }
            
            .customer-info {
                margin-bottom: 2cm;
            }
            
            .invoice-table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 2cm;
            }
            
            .invoice-table th,
            .invoice-table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            
            .invoice-table th {
                background-color: #f5f5f5;
                font-weight: bold;
            }
            
            .totals {
                text-align: right;
                margin-bottom: 2cm;
            }
            
            .total-row {
                font-weight: bold;
                font-size: 14pt;
            }
            
            .footer {
                margin-top: 2cm;
                text-align: center;
                font-size: 10pt;
                color: #666;
                border-top: 1px solid #ddd;
                padding-top: 1cm;
            }
        ''', font_config=self.font_config)
    
    def generate_invoice_pdf(self, invoice: Invoice) -> str:
        """
        Generate PDF for an invoice.
        
        Args:
            invoice: Invoice object
            
        Returns:
            Path to generated PDF file
        """
        # Prepare context data
        context = {
            'invoice': invoice,
            'customer': invoice.customer,
            'items': invoice.items.all(),
            'generated_at': timezone.now(),
            'company_name': 'SaaS Invoice Platform',
            'company_address': '123 Business St, Suite 100, City, State 12345',
            'company_phone': '+1 (555) 123-4567',
            'company_email': 'billing@saas-invoice.com',
        }
        
        # Render HTML template
        html_content = render_to_string('documents/invoice_pdf.html', context)
        
        # Generate PDF
        html = HTML(string=html_content)
        pdf = html.write_pdf(
            stylesheets=[self.base_css],
            font_config=self.font_config
        )
        
        # Save PDF file
        filename = f"invoice_{invoice.number}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(settings.MEDIA_ROOT, 'invoices', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write PDF file
        with open(filepath, 'wb') as f:
            f.write(pdf)
        
        return filepath
    
    def generate_invoice_html(self, invoice: Invoice) -> str:
        """
        Generate HTML for an invoice (for preview).
        
        Args:
            invoice: Invoice object
            
        Returns:
            HTML content
        """
        context = {
            'invoice': invoice,
            'customer': invoice.customer,
            'items': invoice.items.all(),
            'generated_at': timezone.now(),
            'company_name': 'SaaS Invoice Platform',
            'company_address': '123 Business St, Suite 100, City, State 12345',
            'company_phone': '+1 (555) 123-4567',
            'company_email': 'billing@saas-invoice.com',
        }
        
        return render_to_string('documents/invoice_pdf.html', context)


# Global instance
pdf_generator = PDFGenerator() 