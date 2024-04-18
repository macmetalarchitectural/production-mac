/** @odoo-module **/
import core from 'web.core';

odoo.define('e3k_mac_contact_customisation.CalendarScheduleNext', function (require) {
    "use strict";

    var CalendarRenderer = require('web.CalendarRenderer');
    var CalendarView = require('web.CalendarView');
    var viewRegistry = require('web.view_registry');
    const CalendarPopover = require('@calendar/js/calendar_renderer')[Symbol.for("default")].AttendeeCalendarPopover;

    var AttendeeCalendarPopover = CalendarPopover.include({
        events: _.extend({}, CalendarPopover.prototype.events, {
            'click .o_cw_event_done': '_onClickDone',
            'click .o_cw_event_done_schedule_next': '_onClickDoneScheduleNext',
        }),

        _onClickDone: function (ev) {
            ev.preventDefault();
            var self = this;
            this._rpc({
                model: 'calendar.event',
                method: 'action_done',
                args: [[parseInt(this.event.id)]],
            });
        },

        _onClickDoneScheduleNext: function (ev) {

            ev.preventDefault();
            var self = this;
            var partner_ids=self.event.extendedProps.record.partner_ids;
            console.log(partner_ids);

            this._rpc({
                model: 'calendar.event',
                method: 'action_done',
                args: [[parseInt(this.event.id)]],
            }).then(function (result) {
                const action = {
                    type: 'ir.actions.act_window',
                    name: "Schedule activity",
                    res_model: 'calendar.event',
                    view_mode: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                    context: {
                        default_res_model: 'calendar.event',

                        default_activity_ids: false,
                        default_partner_ids: partner_ids,


                    },
                    res_id: false,
                };
                return core.bus.trigger('do-action', {
                    action,
                    options: {
                        on_close: () => {


                        },
                    },
                });

            });
        },
    });
});
