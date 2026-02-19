/** @odoo-module **/

import { NameAndSignature } from "@web/core/signature/name_and_signature";
import { SignatureForm } from "@portal/signature_form/signature_form";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";
import { formatDateTime, parseDateTime, serializeDateTime } from "@web/core/l10n/dates";
import { useDateTimePicker } from "@web/core/datetime/datetime_picker_hook";
import { useState, onWillStart, useRef } from "@odoo/owl";

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
            return;
        }

        // Validate weekday
        if (![1, 2, 3, 4, 5].includes(value.weekday)) {
            this.deliveryState.hasError = true;
            this.deliveryState.errorMessage = _t('Please select a weekday (Monday to Friday).');
            this.deliveryState.date = null;
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
            return;
        }

        // Valid date
        this.deliveryState.date = value;
        this.deliveryState.hasError = false;
        this.deliveryState.errorMessage = '';
    },

    /**
     * Get the selected delivery date (for compatibility)
     */
    getDeliveryDate() {
        return this.deliveryState.date ? serializeDateTime(this.deliveryState.date) : '';
    },

    /**
     * Get delivery date as ISO string
     */
    getDeliveryDateISO() {
        return this.deliveryState.date ? this.deliveryState.date.toISO() : null;
    },

    /**
     * Validate signature including delivery date
     */
    validateSignature() {
        const hasDeliveryDate = !!this.deliveryState.date;
        const name = this.props.signature.name;
        const isSignatureEmpty = this.props.signature.isSignatureEmpty;

        // Update error state reactively
        if (!hasDeliveryDate) {
            this.deliveryState.hasError = true;
            this.deliveryState.errorMessage = _t('Please select a delivery date.');
        }

        // Validate name and signature (let parent handle those)
        const isValid = super.validateSignature ?
            super.validateSignature() :
            (!isSignatureEmpty && !!name);

        return hasDeliveryDate && isValid;
    },
});

/**
 * Patch SignatureForm to handle delivery date in submission (100% OWL)
 */
patch(SignatureForm.prototype, {
    setup() {
        super.setup(...arguments);

        // Add loading state
        if (!this.state.isSubmitting) {
            this.state.isSubmitting = false;
        }

        // Reference to submit button
        this.submitButtonRef = useRef("submitButton");
    },

    /**
     * Override click submit to add delivery date to RPC params (100% OWL)
     */
    async onClickSubmit() {
        // Validate first
        if (this.nameAndSignatureRef?.comp) {
            const comp = this.nameAndSignatureRef.comp;
            if (!comp.validateSignature()) {
                return;
            }
        }

        // Set loading state (reactive)
        this.state.isSubmitting = true;

        try {
            // Get delivery date from NameAndSignature component
            let delivery = null;
            if (this.nameAndSignatureRef?.comp?.getDeliveryDateISO) {
                delivery = this.nameAndSignatureRef.comp.getDeliveryDateISO();
            }

            // Prepare params
            const name = this.signature.name;
            const signature = this.signature.getSignatureImage().split(",")[1];
            const params = { name, signature };

            if (delivery) {
                params.delivery = delivery;
            }

            // Make RPC call
            const data = await rpc(this.props.callUrl, params);

            if (data.force_refresh) {
                if (data.redirect_url) {
                    const { redirect } = await import("@web/core/utils/urls");
                    redirect(data.redirect_url);
                } else {
                    window.location.reload();
                }
                return new Promise(() => {});
            }

            // Update state reactively
            this.state.error = data.error || false;
            this.state.success = !data.error && {
                message: data.message,
                redirectUrl: data.redirect_url,
                redirectMessage: data.redirect_message,
            };
        } catch (error) {
            console.error('Error submitting signature:', error);
            this.state.error = error.message || _t('An error occurred');
        } finally {
            // Reset loading state
            this.state.isSubmitting = false;
        }
    },
});
