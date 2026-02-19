/** @odoo-module **/

import { CalendarCommonRenderer } from "@web/views/calendar/calendar_common/calendar_common_renderer";
import { patch } from "@web/core/utils/patch";

patch(CalendarCommonRenderer.prototype, {
    /**
     * Override get options to customize viewDidMount callback
     */
    get options() {
        const options = super.options;
        const originalViewDidMount = options.viewDidMount;

        options.viewDidMount = ({ el, view }) => {
            // Call original viewDidMount
            originalViewDidMount.call(this, { el, view });

            // Add custom class for stock.picking model in week/day view
            const resModel = this.props.model.resModel;
            const scale = this.props.model.scale;

            if (resModel === 'stock.picking' && (scale === 'week' || scale === 'day')) {
                el.classList.add('e3k_calendar');
            } else {
                el.classList.remove('e3k_calendar');
            }
        };

        return options;
    },

    /**
     * Override onEventContent to customize title for stock.picking
     */
    onEventContent(arg) {
        const { event } = arg;
        const record = this.props.model.records[event.id];
        const resModel = this.props.model.resModel;

        // Use custom display name for stock.picking
        if (record && resModel === 'stock.picking' && record.rawRecord.e3k_custom_display_name) {
            record.title = record.rawRecord.e3k_custom_display_name;
        }

        return super.onEventContent(...arguments);
    },

    /**
     * Override onEventDidMount to build custom DOM for stock.picking events
     */
    onEventDidMount({ el, event }) {
        super.onEventDidMount(...arguments);

        const record = this.props.model.records[event.id];
        const resModel = this.props.model.resModel;

        if (record && resModel === 'stock.picking') {
            // Clear existing content
            const eventMain = el.querySelector('.fc-event-main');
            if (!eventMain) return;

            // Build custom event content
            eventMain.innerHTML = '';

            // Create container with flex layout
            const container = document.createElement('div');
            container.className = 'd-flex align-items-center justify-content-between';
            container.style.cssText = 'margin: 0; height: 100%; padding: 2px 4px;';

            // Create title span
            const titleSpan = document.createElement('span');
            titleSpan.textContent = record.rawRecord.e3k_custom_display_name || record.title;
            titleSpan.style.cssText = 'display: inline-block; margin-right: 8px; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;';

            // Apply custom text color if defined
            if (record.rawRecord.e3k_calendar_text_color) {
                titleSpan.style.color = record.rawRecord.e3k_calendar_text_color;
            }

            container.appendChild(titleSpan);

            // Add black dot indicator for 'assigned' state
            if (record.rawRecord.state === 'assigned') {
                const dot = document.createElement('div');
                dot.style.cssText = 'width: 10px; height: 10px; background-color: black; border-radius: 50%; flex-shrink: 0;';
                container.appendChild(dot);
            }

            eventMain.appendChild(container);

            // Apply custom background color if defined
            if (record.rawRecord.e3k_calendar_color) {
                el.style.backgroundColor = record.rawRecord.e3k_calendar_color;
            }

            // Apply custom text color to entire element if defined
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
