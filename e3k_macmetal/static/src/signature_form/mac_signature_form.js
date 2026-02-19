/** @odoo-module **/

import { NameAndSignature } from "@web/core/signature/name_and_signature";
import { SignatureForm } from "@portal/signature_form/signature_form";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { parseDateTime } from "@web/core/l10n/dates";
import { onWillStart, onMounted, useRef } from "@odoo/owl";

/**
 * Patch NameAndSignature to add delivery date field with date picker
 */
patch(NameAndSignature.prototype, {
    setup() {
        super.setup(...arguments);

        this.deliveryDateRef = useRef("deliveryDate");
        this.paddingDeliveryDays = 0;

        // Fetch padding delivery days from server
        onWillStart(async () => {
            this.paddingDeliveryDays = await rpc('/get_padding_delivery_days');
        });

        // Initialize datepicker after mount
        onMounted(() => {
            if (this.deliveryDateRef.el) {
                this._initDateTimePicker();
            }
        });
    },

    /**
     * Get the selected delivery date
     */
    getDeliveryDate() {
        return this.deliveryDateRef.el ? this.deliveryDateRef.el.value : '';
    },

    /**
     * Initialize date/time picker with moment and datetimepicker
     */
    _initDateTimePicker() {
        const $dateGroup = $(this.deliveryDateRef.el).closest('.o_sign_form_date');

        if (!$dateGroup.length) {
            return;
        }

        const paddingDeliveryDays = this.paddingDeliveryDays || 0;

        // Calculate min date excluding weekends using moment-weekday-calc
        const minDateData = moment(new Date()).isoAddWeekdaysFromSet(
            paddingDeliveryDays,
            [1, 2, 3, 4, 5], // Weekdays Mon to Fri
            [] // Public holidays if needed
        );

        const maxDateData = moment().add(200, "y");

        $dateGroup.datetimepicker({
            format: moment.localeData().longDateFormat('L') + ' ' + moment.localeData().longDateFormat('LT'),
            minDate: minDateData.toISOString(),
            maxDate: maxDateData.toISOString(),
            useCurrent: false,
            viewDate: moment(new Date().toISOString()),
            calendarWeeks: true,
            icons: {
                time: 'fa fa-clock-o',
                date: 'fa fa-calendar',
                next: 'fa fa-chevron-right',
                previous: 'fa fa-chevron-left',
                up: 'fa fa-chevron-up',
                down: 'fa fa-chevron-down',
            },
            locale: moment.locale(),
            allowInputToggle: true,
        });

        // Handle date picker errors
        $dateGroup.on('error.datetimepicker', (err) => {
            if (err.date) {
                const format = moment.localeData().longDateFormat('L') + ' ' + moment.localeData().longDateFormat('LT');
                if (err.date < minDateData) {
                    alert(`The date you selected is lower than the minimum date: ${minDateData.format(format)}`);
                }
                if (err.date > maxDateData) {
                    alert(`The date you selected is greater than the maximum date: ${maxDateData.format(format)}`);
                }
            }
            return false;
        });
    },

    /**
     * Validate signature including delivery date
     */
    validateSignature() {
        const deliveryDate = this.getDeliveryDate();
        const name = this.props.signature.name;
        const isSignatureEmpty = this.props.signature.isSignatureEmpty;

        // Toggle error classes
        if (this.deliveryDateRef.el) {
            const $deliveryGroup = $(this.deliveryDateRef.el).parent();
            $deliveryGroup.toggleClass('o_has_error', !deliveryDate);
            $(this.deliveryDateRef.el).toggleClass('is-invalid', !deliveryDate);
        }

        // Validate name and signature (let parent handle those)
        const isValid = super.validateSignature ? super.validateSignature() : (!isSignatureEmpty && !!name);

        return deliveryDate && isValid;
    },
});

/**
 * Patch SignatureForm to handle delivery date in submission
 */
patch(SignatureForm.prototype, {
    /**
     * Override click submit to add delivery date to RPC params
     */
    async onClickSubmit() {
        if (!this.signature.validateSignature || !this.signature.validateSignature()) {
            // If custom validation exists, use it
            if (this.nameAndSignatureRef && this.nameAndSignatureRef.comp) {
                const comp = this.nameAndSignatureRef.comp;
                if (!comp.validateSignature()) {
                    return;
                }
            }
        }

        const button = document.querySelector('.o_portal_sign_submit');
        if (!button) {
            return super.onClickSubmit(...arguments);
        }

        const icon = button.firstChild ? button.removeChild(button.firstChild) : null;
        const { default: addLoadingEffect } = await import('@web/core/utils/ui');
        const restoreBtnLoading = addLoadingEffect(button);

        // Get delivery date from NameAndSignature component
        let delivery = null;
        if (this.nameAndSignatureRef && this.nameAndSignatureRef.comp && this.nameAndSignatureRef.comp.getDeliveryDate) {
            const deliveryValue = this.nameAndSignatureRef.comp.getDeliveryDate();
            if (deliveryValue) {
                // Parse and convert to ISO format
                const momentDate = moment(deliveryValue, moment.localeData().longDateFormat('L') + ' ' + moment.localeData().longDateFormat('LT'));
                delivery = momentDate.toISOString();
            }
        }

        const name = this.signature.name;
        const signature = this.signature.getSignatureImage().split(",")[1];

        const params = { name, signature };
        if (delivery) {
            params.delivery = delivery;
        }

        try {
            const data = await rpc(this.props.callUrl, params);

            if (data.force_refresh) {
                restoreBtnLoading();
                if (icon) button.prepend(icon);

                if (data.redirect_url) {
                    const { redirect } = await import("@web/core/utils/urls");
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
        } catch (error) {
            console.error('Error submitting signature:', error);
            this.state.error = error.message || 'An error occurred';
        } finally {
            restoreBtnLoading();
            if (icon) button.prepend(icon);
        }
    },
});
