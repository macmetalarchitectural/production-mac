/** @odoo-module **/
import Dialog from 'web.Dialog';
import core from 'web.core';
import time from 'web.time';
import field_utils from 'web.field_utils';
import { patch } from "web.utils";

var _t = core._t;
var QWeb = core.qweb;

import { NameAndSignature } from 'web.name_and_signature';
import { SignatureForm } from 'portal.signature_form';

NameAndSignature.include({
  xmlDependencies: (NameAndSignature.prototype.xmlDependencies || []).concat(
    ["/e3k_macmetal/static/src/xml/signature_form.xml"]
  ),

  willStart: function() {
    var self = this;
    return this._super().then(async function() {
        self.paddingDeliveryDays = await self._rpc({
            route: '/get_padding_delivery_days',
            params: {}
        });
    });
  },

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
    var dateType = "datetime";
    var paddingDeliveryDays = $dateGroup.find('input').data('paddingdays');
    var minDateData = moment(new Date().setDate(new Date().getDate() + paddingDeliveryDays));
    var maxDateData = "";

    var datetimepickerFormat = dateType === 'datetime' ? time.getLangDatetimeFormat() : time.getLangDateFormat();

    var minDate = minDateData ? this._formatDateTime(minDateData, datetimepickerFormat) : moment({ y: 1000 });
    var maxDate = maxDateData ? this._formatDateTime(maxDateData, datetimepickerFormat) : moment().add(200, "y");

    if (dateType === 'date') {
      // Include min and max date in selectable values
      maxDate = moment(maxDate).add(1, "d");
      minDate = moment(minDate).subtract(1, "d");
      disabledDates = [minDate, maxDate];
    }

    $dateGroup.datetimepicker({
      format : datetimepickerFormat,
      minDate: minDate.toISOString(),
      maxDate: maxDate.toISOString(),
      disabledDates: disabledDates,
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

  validateSignature: function () {
    var deliveryDate = this.getDeliveryDate();
    var name = this.getName();
    var isSignatureEmpty = this.isSignatureEmpty();
    this.$nameInput.parent().toggleClass('o_has_error', !name)
      .find('.form-control, .custom-select').toggleClass('is-invalid', !name);
    this.$deliveryDateInput.parent().toggleClass('o_has_error', !deliveryDate)
      .find('.form-control, .custom-select').toggleClass('is-invalid', !deliveryDate);
    this.$signatureGroup.toggleClass('border-danger', isSignatureEmpty);
    return deliveryDate && name && !isSignatureEmpty;
  },

});

patch(SignatureForm.prototype, 'e3k_macmetal.signature_form', {

  _onClickSignSubmit: function (ev) {
    var self = this;
    ev.preventDefault();

    if (!this.nameAndSignature.validateSignature()) {
      return;
    }

    var delivery = this._prepareSubmitDates(this.nameAndSignature.getDeliveryDate(), true);
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
        self.$controls.prepend(QWeb.render('portal.portal_signature_error', {widget: data}));
      } else if (data.success) {
        var $success = QWeb.render('portal.portal_signature_success', {widget: data});
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

  _prepareSubmitDates: function (value, isDateTime) {
    var momentDate = isDateTime ? field_utils.parse.datetime(value, null, {timezone: true}) : field_utils.parse.date(value);
    var formattedDate = momentDate ? momentDate.toJSON() : '';
    return formattedDate;
  },

});