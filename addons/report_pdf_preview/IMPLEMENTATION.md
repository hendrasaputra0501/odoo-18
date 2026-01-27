# Implementation Summary - report_pdf_preview Module

## Problem Statement (in Indonesian)
Saya ingin membuat addons dengan nama report_pdf_preview. Modul ini digunakan saat user menjalankan action print report qweb-pdf, maka akan muncul Dialog Box berisi iframe untuk menampilkan pdf yang berhasil di render.

## Translation
"I want to create an addon named report_pdf_preview. This module is used when a user runs a print report action for qweb-pdf, then a Dialog Box will appear containing an iframe to display the successfully rendered PDF."

## Solution Implemented

### Module Structure
```
report_pdf_preview/
├── __init__.py                          # Empty init file
├── __manifest__.py                      # Module manifest with dependencies and assets
├── README.md                            # Module documentation
├── TESTING.md                           # Testing guide
└── static/src/
    ├── js/
    │   └── pdf_preview_dialog.js       # Main JavaScript component and handler
    └── xml/
        └── pdf_preview_dialog.xml      # OWL template for dialog
```

### Key Components

#### 1. PdfPreviewDialog Component (OWL)
- **Location**: `static/src/js/pdf_preview_dialog.js`
- **Purpose**: Creates a fullscreen dialog with an iframe showing the PDF
- **Features**:
  - Loading spinner while PDF renders
  - Error handling with user notifications
  - Download button to save PDF
  - Close button to dismiss dialog

#### 2. Report Handler
- **Location**: `static/src/js/pdf_preview_dialog.js` (pdfPreviewReportHandler function)
- **Purpose**: Intercepts qweb-pdf report actions before default download behavior
- **Registration**: Added to `"ir.actions.report handlers"` registry with sequence 100
- **Logic**:
  1. Checks if action type is `qweb-pdf`
  2. Builds PDF preview URL with proper parameters (active_ids, context, data)
  3. Opens PdfPreviewDialog with PDF URL
  4. Returns `true` to prevent default handler from executing

#### 3. Helper Functions
- **hasCustomData(action)**: Checks if action has custom wizard data
- **buildReportUrl(baseUrl, action)**: Builds report URL with parameters (DRY principle)

### Technical Implementation Details

#### Dialog Component Integration
The module uses Odoo's standard Dialog component from `@web/core/dialog/dialog`:
- Size: fullscreen for better PDF viewing
- Footer: Custom buttons (Download and Close)
- Error handling: Notifications via notification service
- State management: OWL reactive state (loading, error)

#### Report Action Interception
The handler is registered in the `"ir.actions.report handlers"` registry:
```javascript
registry.category("ir.actions.report handlers")
    .add("pdf_preview_handler", pdfPreviewReportHandler, {
        sequence: 100,
    });
```

The action service calls handlers in sequence order. When a handler returns `true`, processing stops and default behavior is prevented.

#### URL Building
Report URLs are constructed following Odoo's conventions:
- Base format: `/report/pdf/{report_name}`
- With active IDs: `/report/pdf/{report_name}/{id1,id2,...}`
- With custom data: `/report/pdf/{report_name}?options={data}&context={context}`

#### Download Mechanism
Uses Odoo's download utility with the standard `/report/download` endpoint:
```javascript
await download({
    url: "/report/download",
    data: {
        data: JSON.stringify([reportUrl, reportType]),
        context: JSON.stringify(userContext),
    },
});
```

### Error Handling
1. **Iframe Load Failure**: 
   - Shows error message in dialog
   - Displays notification to user
   - Sets hasError state to show error UI

2. **Download Failure**:
   - Try-catch around download call
   - Notification to user on failure
   - Graceful degradation

### Browser Compatibility
The iframe PDF preview works in modern browsers that support inline PDF rendering:
- Chrome/Edge: Native PDF viewer
- Firefox: Native PDF viewer
- Safari: Native PDF viewer
- Other browsers may download instead of showing inline (fallback behavior)

### Performance Considerations
1. **Loading State**: Prevents user interaction until PDF is ready
2. **Conditional Rendering**: Iframe only rendered when needed
3. **Error States**: Clear feedback prevents user confusion
4. **Single Render**: PDF generated once, can be downloaded multiple times

### Dependencies
- **web** module: Provides Dialog component, services, and utilities
- No external libraries required
- Uses standard Odoo 18 patterns

## Usage
1. Install the module: `./odoo-bin -i report_pdf_preview`
2. No configuration needed
3. All qweb-pdf reports automatically show preview dialog
4. Users can preview before downloading

## Testing
See TESTING.md for detailed testing instructions. Test with:
- Sales Orders (Print Quotation)
- Invoices (Print Invoice)
- Any model with PDF reports

## Architecture Decisions

### Why Handler Registry Instead of Monkey Patching?
- Cleaner, Odoo-native approach
- Allows other modules to add handlers
- Easy to enable/disable via module install/uninstall
- No conflicts with core updates

### Why Fullscreen Dialog?
- PDFs need space to be readable
- Better user experience for document preview
- Matches common PDF viewer patterns

### Why Iframe Instead of PDF.js?
- Simpler implementation
- Uses browser's native PDF rendering
- Better performance (no external library)
- Consistent with Odoo's HTML report preview

## Limitations
1. Preview depends on browser PDF support
2. Some PDF features (annotations, forms) may not work in iframe
3. Very large PDFs may take time to load
4. Mobile browsers may have limited PDF support

## Future Enhancements
- Add print button (trigger browser print dialog)
- Add zoom controls
- Add page navigation for multi-page PDFs
- Add option to disable preview per report
- Add preview for qweb-text reports

## Security Considerations
- No user input processing (XSS safe)
- Uses Odoo's standard download mechanism
- No new security vulnerabilities introduced
- Follows Odoo's access control (reports only accessible if user has permission)

## Maintenance
- Minimal maintenance required
- No database migrations needed
- Pure JavaScript/OWL implementation
- Compatible with Odoo 18.0

## Credits
Module created for Odoo 18.0 following community best practices.
