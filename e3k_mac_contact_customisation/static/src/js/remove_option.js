/** @odoo-module **/
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

/**
 * Force the delete button to be available in all FormViewDialogs.
 * Equivalent to Odoo 15: FormViewDialog.include({ init: (parent, opts) => { opts.deletable = true } })
 */
patch(FormViewDialog.prototype, {
    setup() {
        super.setup(...arguments);
        this.macOrm = useService("orm");
        // Enable delete if not already provided by the parent context
        if (!this.props.removeRecord && this.props.resId) {
            this.viewProps.removeRecord = async (record) => {
                await this.macOrm.unlink(this.props.resModel, [record.resId]);
                this.props.close();
            };
        }
    },
});
