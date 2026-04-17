/** @odoo-module **/
import { X2ManyField } from "@web/views/fields/x2many/x2many_field";
import { patch } from "@web/core/utils/patch";

/**
 * For res.partner One2many fields (contact_ids, delivery_address_ids, etc.),
 * clicking a kanban card navigates directly to the full form view
 * instead of opening the X2ManyFieldDialog popup.
 * Intercepts X2ManyField.openRecord — the exact point where the dialog would be triggered.
 */
patch(X2ManyField.prototype, {
    async openRecord(record) {
        if (this.list.resModel === "res.partner" && record.resId) {
            return this.switchToForm(record, {});
        }
        return super.openRecord(record);
    },
});
