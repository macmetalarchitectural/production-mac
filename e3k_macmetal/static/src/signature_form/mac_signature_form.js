/** @odoo-module **/

import { NameAndSignature } from "@web/core/signature/name_and_signature";
import { SignatureForm } from "@portal/signature_form/signature_form";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";
import { formatDateTime, serializeDateTime } from "@web/core/l10n/dates";
import { redirect } from "@web/core/utils/urls";
import { useDateTimePicker } from "@web/core/datetime/datetime_picker_hook";
import { useState, onWillStart } from "@odoo/owl";

const { DateTime } = luxon;

/**
 * Add weekdays to a date, excluding weekends
 * @param {DateTime} startDate - Luxon DateTime object
 * @param {number} days - Number of weekdays to add
 * @param {number[]} weekdays - Array of allowed weekdays (1=Mon, 5=Fri)
 * @returns {DateTime}
 */
function addWeekdays(startDate, days, weekdays = [1, 2, 3, 4, 5]) {
    let current = startDate;
    let remaining = days;

    while (remaining > 0) {
        current = current.plus({ days: 1 });
        if (weekdays.includes(current.weekday)) {
            remaining--;
        }
    }

    return current;
}

/**
 * Patch NameAndSignature to add delivery date field with OWL date picker
 */
patch(NameAndSignature.prototype, {
    get deliveryDatePlaceholder() {
        return _t("Select date and time");
    },

    setup() {
        super.setup(...arguments);

        // OWL reactive state
        this.deliveryState = useState({
            date: null,
            hasError: false,
            errorMessage: '',
            minDate: null,
            maxDate: null,
            paddingDays: 0,
        });

        // Fetch padding delivery days from server
        onWillStart(async () => {
            this.deliveryState.paddingDays = await rpc('/get_padding_delivery_days');

            // Calculate min/max dates
            const now = DateTime.now();
            this.deliveryState.minDate = addWeekdays(
                now,
                this.deliveryState.paddingDays,
                [1, 2, 3, 4, 5]
            );
            this.deliveryState.maxDate = now.plus({ years: 200 });
        });

        // Use Odoo's native DateTimePicker hook
        this.dateTimePicker = useDateTimePicker({
            startDateRefName: "deliveryDate",
            pickerProps: () => ({
                type: "datetime",
                value: this.deliveryState.date,
                minDate: this.deliveryState.minDate,
                maxDate: this.deliveryState.maxDate,
            }),
            onApply: (value) => this.onDeliveryDateChange(value),
        });
    },

    /**
     * Handle delivery date change
     * @param {DateTime} value
     */
    onDeliveryDateChange(value) {
        if (!value) {
            this.deliveryState.date = null;
            this.deliveryState.hasError = false;
            this.props.signature.deliveryDate = null;
            return;
        }

        // Validate weekday
        if (![1, 2, 3, 4, 5].includes(value.weekday)) {
            this.deliveryState.hasError = true;
            this.deliveryState.errorMessage = _t('Please select a weekday (Monday to Friday).');
            this.deliveryState.date = null;
            this.props.signature.deliveryDate = null;
            return;
        }

        // Validate min date
        if (value < this.deliveryState.minDate) {
            this.deliveryState.hasError = true;
            this.deliveryState.errorMessage = _t(
                'The date must be at least %s',
                formatDateTime(this.deliveryState.minDate)
            );
            this.deliveryState.date = null;
            this.props.signature.deliveryDate = null;
            return;
        }

        // Valid date — store locally and on shared signature state
        this.deliveryState.date = value;
        this.deliveryState.hasError = false;
        this.deliveryState.errorMessage = '';
        this.props.signature.deliveryDate = value;
    },

});

/**
 * Patch SignatureForm to handle delivery date in submission (100% OWL)
 */
patch(SignatureForm.prototype, {
    setup() {
        super.setup(...arguments);
        // Extend shared signature state with deliveryDate
        this.signature.deliveryDate = null;
    },

    /**
     * Override click submit to add delivery date to RPC params.
     * Delivery date is read from this.signature.deliveryDate, written
     * by the NameAndSignature patch via this.props.signature.deliveryDate.
     */
    async onClickSubmit() {
        // Validate delivery date before proceeding
        if (!this.signature.deliveryDate) {
            this.state.error = _t('Please select a delivery date.');
            return;
        }

        const name = this.signature.name;
        const signature = this.signature.getSignatureImage().split(",")[1];
        const delivery = serializeDateTime(this.signature.deliveryDate);
        const data = await rpc(this.props.callUrl, { name, signature, delivery });

        if (data.force_refresh) {
            if (data.redirect_url) {
                redirect(data.redirect_url);
            } else {
                window.location.reload();
            }
            return new Promise(() => {});
        }

        this.state.error = data.error || false;
        this.state.success = !data.error && {
            message: data.message,
            redirectUrl: data.redirect_url,
            redirectMessage: data.redirect_message,
        };
    },
});
