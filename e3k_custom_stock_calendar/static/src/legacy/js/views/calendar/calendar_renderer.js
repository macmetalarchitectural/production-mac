/** @odoo-module **/
import { qweb, _t } from 'web.core';
import AbstractRenderer from 'web.CalendarRenderer';

AbstractRenderer.include({

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

