/** @odoo-module **/
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onMounted } from "@odoo/owl";

/**
 * When a child contact (res.partner) is clicked from a company form,
 * redirect to the full form view instead of opening a popup dialog.
 */
patch(FormViewDialog.prototype, {
    setup() {
        super.setup(...arguments);
        if (this.props.resModel === "res.partner" && this.props.resId) {
            const actionService = useService("action");
            onMounted(() => {
                actionService.doAction({
                    type: "ir.actions.act_window",
                    res_model: "res.partner",
                    res_id: this.props.resId,
                    views: [[false, "form"]],
                    target: "current",
                });
            });
        }
    },
});
