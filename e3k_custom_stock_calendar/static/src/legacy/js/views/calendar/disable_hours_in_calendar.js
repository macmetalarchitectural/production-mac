odoo.define('e3k_custom_stock_calendar.CalendarRenderer', function(require) {
    'use strict';

    var CalendarRenderer = require("web.CalendarRenderer");


    CalendarRenderer.include({
        start: function () {
            var res = this._super();
            $(this.calendar.el).addClass('e3k_calendar');
            return res;
        },
    });


});
