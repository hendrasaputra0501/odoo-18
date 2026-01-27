# Report PDF Preview

## Description

This module enhances the PDF report printing functionality in Odoo by displaying a preview dialog before the actual download.

When a user clicks on a "Print" button for a qweb-pdf report, instead of directly downloading the PDF file, a Dialog Box will appear with an iframe showing the rendered PDF. The user can then:
- Preview the PDF content
- Download the PDF using the "Download PDF" button
- Close the dialog without downloading

## Features

- **PDF Preview Dialog**: Shows a fullscreen dialog with the PDF rendered in an iframe
- **Download Button**: Allows users to download the PDF after preview
- **Seamless Integration**: Works with all existing qweb-pdf reports without modification
- **Loading Indicator**: Shows a loading spinner while the PDF is being rendered

## Technical Details

### Components

1. **PdfPreviewDialog**: An OWL component that extends Dialog to show PDF preview
2. **pdfPreviewReportHandler**: A report action handler registered in the "ir.actions.report handlers" registry

### How it Works

1. When a `ir.actions.report` action with `report_type='qweb-pdf'` is triggered
2. The `pdfPreviewReportHandler` intercepts the action before the default handler
3. It builds the PDF URL and download parameters
4. Opens the `PdfPreviewDialog` with the PDF loaded in an iframe
5. User can preview and download from the dialog

### Dependencies

- `web` module (for Dialog component and services)

## Usage

Simply install the module and all PDF reports will automatically show a preview dialog.

No configuration needed.

## Credits

Module developed for Odoo 18.0
