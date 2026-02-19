/** @odoo-module **/

/**
 * Calendar customization module for stock.picking
 *
 * This module extends Odoo's CalendarCommonRenderer to customize event rendering
 * for the stock.picking model with specific features:
 * - Custom title display (e3k_custom_display_name)
 * - Visual indicator for 'assigned' state (black dot)
 * - Border management (red for flexible_date, black otherwise)
 * - Custom colors (background and text)
 * - Hide hour column in week/day view
 *
 * Architecture:
 * - Uses a custom OWL template (e3k_mac_stock_calendar.StockCalendarEvent)
 * - Styles defined in SCSS (stock_calendar.scss)
 * - Minimal DOM manipulation (only for dynamic colors)
 */

import { CalendarCommonRenderer } from "@web/views/calendar/calendar_common/calendar_common_renderer";
import { patch } from "@web/core/utils/patch";
import { renderToFragment } from "@web/core/utils/render";

patch(CalendarCommonRenderer.prototype, {
    /**
     * Override options getter to customize viewDidMount callback
     *
     * This method is called by FullCalendar to get calendar configuration.
     * We intercept viewDidMount to add a custom CSS class 'e3k_calendar'
     * on the calendar container when displaying stock.picking in week/day view.
     *
     * @returns {Object} FullCalendar configuration options with custom viewDidMount
     *
     * Behavior:
     * - First calls original viewDidMount to preserve default behavior
     * - Adds 'e3k_calendar' class if: resModel === 'stock.picking' AND (scale === 'week' OR 'day')
     * - This class allows hiding the hour column via CSS (see stock_calendar.scss)
     */
    get options() {
        const options = super.options;
        const originalViewDidMount = options.viewDidMount;

        options.viewDidMount = ({ el, view }) => {
            // Call original viewDidMount to preserve Odoo standard behavior
            originalViewDidMount.call(this, { el, view });

            // Get model and display scale
            const resModel = this.props.model.resModel;
            const scale = this.props.model.scale;

            // Add custom class only for stock.picking in week/day view
            if (resModel === 'stock.picking' && (scale === 'week' || scale === 'day')) {
                el.classList.add('e3k_calendar');
            } else {
                el.classList.remove('e3k_calendar');
            }
        };

        return options;
    },

    /**
     * Override convertRecordToEvent to enrich event data
     *
     * This method is called for each record before rendering in the calendar.
     * It transforms an Odoo record into a FullCalendar event object.
     *
     * For stock.picking, we add custom properties that will be used
     * in the XML template and for CSS classes:
     *
     * @param {Object} record - Odoo record to convert
     * @returns {Object} Event object enriched with e3k_* properties
     *
     * Added properties:
     * - e3k_display_name: Custom name to display (fallback to title)
     * - e3k_show_assigned_dot: Boolean to show black dot (state === 'assigned')
     * - e3k_flexible_date: Boolean to determine border color
     * - e3k_calendar_color: Custom background color
     * - e3k_calendar_text_color: Custom text color
     *
     * This "OWL-like" approach pre-calculates data for the template, avoiding
     * business logic in XML templates.
     */
    convertRecordToEvent(record) {
        const event = super.convertRecordToEvent(record);

        if (this.props.model.resModel === 'stock.picking' && record.rawRecord) {
            // Enrich event with custom data
            event.e3k_display_name = record.rawRecord.e3k_custom_display_name || record.title;
            event.e3k_show_assigned_dot = record.rawRecord.state === 'assigned';
            event.e3k_flexible_date = record.rawRecord.flexible_date;
            event.e3k_calendar_color = record.rawRecord.e3k_calendar_color;
            event.e3k_calendar_text_color = record.rawRecord.e3k_calendar_text_color;
        }

        return event;
    },

    /**
     * Override onEventContent to use custom OWL template
     *
     * This method is called by FullCalendar to generate HTML content for each event.
     * This is where we inject our custom template for stock.picking.
     *
     * @param {Object} arg - Object containing FullCalendar event
     * @param {Object} arg.event - The event to render
     * @returns {Object|undefined} Object with domNodes (HTML fragments) or undefined for default rendering
     *
     * Process:
     * 1. Check if it's a stock.picking
     * 2. Use renderToFragment() to render 'e3k_mac_stock_calendar.StockCalendarEvent' template
     * 3. Pass record data + computed properties to template
     * 4. Return generated domNodes that FullCalendar will inject into DOM
     *
     * The XML template receives:
     * - All record properties (via ...record)
     * - startTime / endTime: Formatted hours
     * - e3k_display_name: Custom name to display
     * - e3k_show_assigned_dot: Whether to show black dot
     */
    onEventContent(arg) {
        const { event } = arg;
        const record = this.props.model.records[event.id];
        const resModel = this.props.model.resModel;

        if (record && resModel === 'stock.picking') {
            // Render custom OWL template with enriched data
            const fragment = renderToFragment('e3k_mac_stock_calendar.StockCalendarEvent', {
                ...record,
                startTime: this.getStartTime(record),
                endTime: this.getEndTime(record),
                e3k_display_name: record.rawRecord.e3k_custom_display_name || record.title,
                e3k_show_assigned_dot: record.rawRecord.state === 'assigned',
            });
            return { domNodes: fragment.children };
        }

        return super.onEventContent(...arguments);
    },

    /**
     * Override eventClassNames to manage custom CSS classes
     *
     * This method is called by FullCalendar to determine CSS classes to apply
     * on the event's <a> element (parent tag containing the event).
     *
     * @param {Object} params - FullCalendar parameters
     * @param {HTMLElement} params.el - Event DOM element
     * @param {Object} params.event - FullCalendar event object
     * @returns {Array<string>} List of CSS classes to apply
     *
     * Behavior for stock.picking:
     * 1. Remove default Odoo classes 'o_calendar_color_*' that apply predefined colors
     * 2. Add 'e3k_stock_event': base class with default black border (see SCSS)
     * 3. Conditionally add 'e3k_flexible_date': changes border to red (see SCSS)
     *
     * This CSS approach avoids inline styles and allows declarative style management.
     * Borders are handled in CSS, only dynamic colors (from DB) remain inline.
     */
    eventClassNames({ el, event }) {
        const classesToAdd = super.eventClassNames(...arguments);
        const record = this.props.model.records[event.id];
        const resModel = this.props.model.resModel;

        if (record && resModel === 'stock.picking') {
            // Filter out Odoo default classes
            const filteredClasses = classesToAdd.filter(cls => !cls.startsWith('o_calendar_color_'));

            // Add base class for stock.picking (black border)
            filteredClasses.push('e3k_stock_event');

            // Conditionally add class for red border
            if (record.rawRecord.flexible_date) {
                filteredClasses.push('e3k_flexible_date');
            }

            return filteredClasses;
        }

        return classesToAdd;
    },

    /**
     * Override onEventDidMount to apply dynamic styles
     *
     * This method is called by FullCalendar after the event is mounted in DOM.
     * This is the only place where we do imperative DOM manipulation.
     *
     * @param {Object} params - FullCalendar parameters
     * @param {HTMLElement} params.el - Event DOM element
     * @param {Object} params.event - FullCalendar event object
     *
     * Responsibility:
     * Apply ONLY custom colors from database that cannot be handled with static CSS:
     * - e3k_calendar_color: Custom background color (DB field)
     * - e3k_calendar_text_color: Custom text color (DB field)
     *
     * Process:
     * 1. Find parent <a> element with .closest('.fc-event')
     * 2. Apply custom colors as inline styles if defined
     *
     * Note: Borders and HTML structure are handled by CSS/Template,
     * this method ONLY handles dynamic colors.
     *
     * This approach minimizes DOM manipulation and follows OWL principles:
     * - XML template for structure
     * - CSS for static styles
     * - JS only for dynamic styles impossible in CSS
     */
    onEventDidMount({ el, event }) {
        super.onEventDidMount(...arguments);

        const record = this.props.model.records[event.id];
        const resModel = this.props.model.resModel;

        if (record && resModel === 'stock.picking') {
            // Get parent <a> element containing the event
            const fcEventLink = el.closest('.fc-event');
            if (fcEventLink) {
                // Apply custom background color (impossible with static CSS)
                if (record.rawRecord.e3k_calendar_color) {
                    fcEventLink.style.backgroundColor = record.rawRecord.e3k_calendar_color;
                }

                // Apply custom text color (impossible with static CSS)
                if (record.rawRecord.e3k_calendar_text_color) {
                    fcEventLink.style.color = record.rawRecord.e3k_calendar_text_color;
                }
            }
        }
    },
});
