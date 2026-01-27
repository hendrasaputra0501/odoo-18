/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { download } from "@web/core/network/download";
import { useService } from "@web/core/utils/hooks";

/**
 * PDF Preview Dialog Component
 * Displays a PDF in an iframe within a modal dialog
 */
export class PdfPreviewDialog extends Component {
    static template = "report_pdf_preview.PdfPreviewDialog";
    static components = { Dialog };
    static props = {
        pdfUrl: String,
        title: { type: String, optional: true },
        downloadUrl: String,
        downloadData: Object,
        close: Function,
    };

    setup() {
        this.notification = useService("notification");
        this.state = useState({
            isLoading: true,
            hasError: false,
        });
    }

    onIframeLoad() {
        this.state.isLoading = false;
    }

    onIframeError() {
        this.state.isLoading = false;
        this.state.hasError = true;
        this.notification.add(_t("Failed to load PDF preview"), {
            type: "danger",
        });
    }

    async downloadPdf() {
        try {
            await download({
                url: this.props.downloadUrl,
                data: this.props.downloadData,
            });
        } catch (error) {
            this.notification.add(_t("Failed to download PDF"), {
                type: "danger",
            });
        }
    }

    get dialogTitle() {
        return this.props.title || _t("Report Preview");
    }
}

/**
 * Helper function to check if action has custom data
 */
function hasCustomData(action) {
    return action.data && Object.keys(action.data).length > 0;
}

/**
 * Helper function to build report URL with parameters
 */
function buildReportUrl(baseUrl, action) {
    const actionContext = action.context || {};
    
    if (hasCustomData(action)) {
        const optionsParam = encodeURIComponent(JSON.stringify(action.data));
        const contextParam = encodeURIComponent(JSON.stringify(actionContext));
        return `${baseUrl}?options=${optionsParam}&context=${contextParam}`;
    } else if (actionContext.active_ids) {
        return `${baseUrl}/${actionContext.active_ids.join(",")}`;
    }
    return baseUrl;
}

/**
 * Report handler that intercepts qweb-pdf actions and shows preview dialog
 */
async function pdfPreviewReportHandler(action, options, env) {
    if (action.report_type === "qweb-pdf") {
        const actionContext = action.context || {};
        
        // Build the PDF URL (used for both preview and download)
        const reportUrl = buildReportUrl(`/report/pdf/${action.report_name}`, action);
        
        // Download data format follows Odoo's expected structure: [report_url, report_type]
        const downloadData = {
            data: JSON.stringify([reportUrl, action.report_type]),
            context: JSON.stringify({ ...env.services.user.context, ...actionContext }),
        };

        // Show the dialog
        env.services.dialog.add(PdfPreviewDialog, {
            pdfUrl: reportUrl,
            title: action.display_name || action.name,
            downloadUrl: "/report/download",
            downloadData,
        });

        return true; // Handler processed the action
    }
    return false; // Let other handlers process it
}

// Register the handler with priority 100 (will run before default handler)
registry.category("ir.actions.report handlers").add("pdf_preview_handler", pdfPreviewReportHandler, {
    sequence: 100,
});
