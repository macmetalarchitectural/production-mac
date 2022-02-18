/** @odoo-module **/

import Dialog from 'web.Dialog';
import core from 'web.core';
import time from 'web.time';
import field_utils from 'web.field_utils';
import { patch } from "web.utils";

var _t = core._t;

import { NameAndSignature } from 'web.name_and_signature';
import { SignatureForm } from 'portal.signature_form';

NameAndSignature.include({
  xmlDependencies: (NameAndSignature.prototype.xmlDependencies || []).concat(
    ["/e3k_macmetal/static/src/xml/signature_form.xml"]
  ),

  start: function () {
    var self = this;
    return this._super.apply(this, arguments).then(function () {
      self.$deliveryDateInput = self.$('.o_web_sign_delivery_date');
      self.$('div.o_sign_form_date').each(function () {
        self._initDateTimePicker($(this));
      });
    });
  },

  getDeliveryDate: function () {
    return this.$deliveryDateInput.val();
  },

  _initDateTimePicker: function ($dateGroup) {
    var disabledDates = [];
    var dateType = "date";
    var minDateData = moment(new Date().setDate(new Date().getDate() + 7)).format("YYYY-MM-DD");;
    var maxDateData = "";
    
    var datetimepickerFormat = dateType === 'datetime' ? time.getLangDatetimeFormat() : time.getLangDateFormat();
    
    var minDate = minDateData
    ? this._formatDateTime(minDateData, datetimepickerFormat)
    : moment({ y: 1000 });
    
    var maxDate = maxDateData
    ? this._formatDateTime(maxDateData, datetimepickerFormat)
    : moment().add(200, "y");
    
    if (dateType === 'date') {
      // Include min and max date in selectable values
      maxDate = moment(maxDate).add(1, "d");
      minDate = moment(minDate).subtract(1, "d");
      disabledDates = [minDate, maxDate];
    }

    $dateGroup.datetimepicker({
      format : datetimepickerFormat,
      minDate: minDate,
      maxDate: maxDate,
      disabledDates: disabledDates,
      useCurrent: false,
      viewDate: moment(new Date()).hours(minDate.hours()).minutes(minDate.minutes()).seconds(minDate.seconds()).milliseconds(minDate.milliseconds()),
      calendarWeeks: true,
      icons: {
        time: 'fa fa-clock-o',
        date: 'fa fa-calendar',
        next: 'fa fa-chevron-right',
        previous: 'fa fa-chevron-left',
        up: 'fa fa-chevron-up',
        down: 'fa fa-chevron-down',
      },
      locale : moment.locale(),
      allowInputToggle: true,
    });

    $dateGroup.on('error.datetimepicker', function (err) {
      if (err.date) {
        if (err.date < minDate) {
          Dialog.alert(this, _t('The date you selected is lower than the minimum date: ') + minDate.format(datetimepickerFormat));
        }

        if (err.date > maxDate) {
          Dialog.alert(this, _t('The date you selected is greater than the maximum date: ') + maxDate.format(datetimepickerFormat));
        }
      }
      return false;
    });
  },

  _formatDateTime: function (datetimeValue, format){
    return moment(field_utils.format.datetime(moment(datetimeValue), null, {timezone: true}), format);
  },

});

patch(SignatureForm.prototype, 'e3k_macmetal.signature_form', {

  _onClickSignSubmit: function (ev) {
    var self = this;
    ev.preventDefault();

    if (!this.nameAndSignature.validateSignature()) {
      return;
    }

    var delivery = this.nameAndSignature.getDeliveryDate();
    var name = this.nameAndSignature.getName();
    var signature = this.nameAndSignature.getSignatureImage()[1];

    return this._rpc({
      route: this.callUrl,
      params: _.extend(this.rpcParams, {
        'delivery': delivery,
        'name': name,
        'signature': signature,
      }),
    }).then(function (data) {
      if (data.error) {
        self.$('.o_portal_sign_error_msg').remove();
        self.$controls.prepend(qweb.render('portal.portal_signature_error', {widget: data}));
      } else if (data.success) {
        var $success = qweb.render('portal.portal_signature_success', {widget: data});
        self.$el.empty().append($success);
      }
      if (data.force_refresh) {
        if (data.redirect_url) {
          window.location = data.redirect_url;
        } else {
          window.location.reload();
        }
        // no resolve if we reload the page
        return new Promise(function () { });
      }
    });
  },

});