/* E3K FOR MAC METAL global FullCalendar */
odoo.define('e3k_custom_stock_calendar.CalendarRenderer', function (require) {
"use strict";

var CalendarRenderer = require('web.CalendarRenderer');



return CalendarRenderer.extend({

    _eventRender: function (event) {
        var qweb_context = {
            event: event,
            record: event.extendedProps.record,
            color: this.getColor(event.extendedProps.color_index),
            showTime: !this.hideTime && event.extendedProps.showTime,
            showLocation: this.state.scale !== 'month'
        };
        qweb_context.record.model = this.model;

        if (_.isEmpty(qweb_context.record)) {
            return '';
        } else {
            return qweb.render(this.config.eventTemplate, qweb_context);
        }
    },

});

});
