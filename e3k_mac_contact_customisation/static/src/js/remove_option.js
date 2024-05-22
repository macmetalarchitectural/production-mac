/** @odoo-module **/
import config from 'web.config';
import core from 'web.core';
import Dialog from 'web.Dialog';
import dom from 'web.dom';
import view_registry from 'web.view_registry';
import select_create_controllers_registry from 'web.select_create_controllers_registry';
var _t = core._t;
import { FormViewDialog } from 'web.view_dialogs';


var MacFormViewDialog = FormViewDialog.include({

    init: function (parent, options) {
        options.deletable = true;
        this._super(parent, options);
    },



});