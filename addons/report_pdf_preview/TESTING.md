# Testing Guide for report_pdf_preview

## Installation

1. Start Odoo server:
```bash
./odoo-bin -d your_database -i report_pdf_preview
```

Or if Odoo is already running, install via UI:
- Go to Apps
- Search for "Report PDF Preview"
- Click Install

## Testing the Module

### Method 1: Using Sales Order Report

1. Go to Sales app
2. Open or create a Sales Order
3. Click the "Print" dropdown button
4. Select "Quotation / Order"
5. A dialog should appear with the PDF preview in an iframe
6. You can download the PDF using the "Download PDF" button
7. Or close the dialog without downloading

### Method 2: Using Invoice Report

1. Go to Accounting app (if installed)
2. Open or create an invoice
3. Click the "Print" button
4. Select "Print Invoice"
5. The preview dialog should appear

### Method 3: Any PDF Report

The module works with any report that has `report_type='qweb-pdf'`. Simply trigger any print action and the preview dialog will appear instead of directly downloading the PDF.

## Expected Behavior

- When printing a PDF report, a fullscreen dialog appears
- The dialog shows a loading spinner while the PDF is being rendered
- Once loaded, the PDF is displayed in an iframe
- A "Download PDF" button allows downloading the report
- A "Close" button closes the dialog without downloading

## Troubleshooting

### Dialog doesn't appear
- Check browser console for JavaScript errors
- Ensure the module is installed and Odoo assets are rebuilt
- Try clearing browser cache and reloading

### PDF doesn't render in iframe
- Check if wkhtmltopdf is installed on the server
- Check server logs for PDF generation errors
- Some browsers may block PDF rendering in iframes - try a different browser

### Module not visible
- Ensure the module is in the addons path
- Restart Odoo server after placing the module
- Update the apps list: Apps menu → Update Apps List
