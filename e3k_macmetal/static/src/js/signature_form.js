odoo.define('e3k_macmetal.signature_form', function (require) {
  "use strict";

  var NameAndSignature = require('web.name_and_signature').NameAndSignature;
  var SignatureForm = require('portal.signature_form').SignatureForm;
  var core = require('web.core');
  var qweb = core.qweb;

  NameAndSignature.include({
    xmlDependencies: (NameAndSignature.prototype.xmlDependencies || []).concat(
      ["/e3k_macmetal/static/src/xml/signature_form.xml"]
    ),
    start: function () {
      this.$deliveryDateInput = this.$('.o_web_sign_delivery_input');
      return this._super.apply(this, arguments);
    },

    getDeliveryDate: function () {
      return this.$deliveryDateInput.val();
    },
  });

  SignatureForm.include({
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
});