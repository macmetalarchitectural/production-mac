/** @odoo-module **/

import { CalendarCommonRenderer } from "@web/views/calendar/calendar_common/calendar_common_renderer";
import { patch } from "@web/core/utils/patch";

patch(CalendarCommonRenderer.prototype, {
    /**
     * Override to add custom class for stock.picking calendar in week/day mode
     * This allows hiding the time column via CSS
     */
    setup() {
        super.setup(...arguments);

        // Store the original viewDidMount to extend it
        const originalViewDidMount = this.viewDidMount.bind(this);

        this.viewDidMount = ({ el, view }) => {
            // Call original viewDidMount
            originalViewDidMount({ el, view });

            // Add custom class for stock.picking model in week/day view
            const resModel = this.props.model.resModel;
            const scale = this.props.model.scale;

            if (resModel === 'stock.picking' && (scale === 'week' || scale === 'day')) {
                el.classList.add('e3k_calendar');
            } else {
                el.classList.remove('e3k_calendar');
            }
        };
    },

    /**
     * Override eventDidMount to apply custom styles for stock.picking
     */
    onEventDidMount({ el, event }) {
        super.onEventDidMount(...arguments);

        const record = this.props.model.records[event.id];
        const resModel = this.props.model.resModel;

        if (record && resModel === 'stock.picking') {
            // Apply custom background color if defined
            if (record.rawRecord.e3k_calendar_color) {
                el.style.backgroundColor = record.rawRecord.e3k_calendar_color;
            }

            // Apply custom text color if defined
            if (record.rawRecord.e3k_calendar_text_color) {
                el.style.color = record.rawRecord.e3k_calendar_text_color;
            }

            // Add red border if flexible_date is true
            if (record.rawRecord.flexible_date) {
                el.style.border = '2px solid red';
            }
        }
    },
});
