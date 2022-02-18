odoo.define("aged_partner_balance_invoice_date", function (require) {
"use strict";

require("account_reports.account_report").include({
    render_searchview_buttons() {
        this._super.apply(this, arguments);
        if (this.report_options.use_maturity_date !== undefined){
            this.setupMaturityDateOption();
        }
        if (this.report_options.use_account_currency !== undefined){
            this.setupAccountCurrencyOption();
        }
        if (this.report_options.available_accounts){
            this.setupAvailableAccountsOption();
        }
    },
    /**
     * Setup the maturity date option.
     *
     * This option enables selecting between `Maturity Date` and `Invoice Date`.
     */
    setupMaturityDateOption(){
        var items = this.$searchview_buttons.find(".o_account_reports__reference_date");
        items.off("click");
        items.bind("click", (event) => {
            var value = $(event.target).parents("li").data("value");
            this.report_options.use_maturity_date = value === "maturity_date";
            this.reload();
        });
    },
    /**
     * Setup the account currency option.
     *
     * This option enables selecting between `Company Currency` and `Account Currency`.
     */
    setupAccountCurrencyOption(){
        var items = this.$searchview_buttons.find(".o_account_reports__reference_currency");
        items.off("click");
        items.bind("click", (event) => {
            var value = $(event.target).parents("li").data("value");
            this.report_options.use_account_currency = value === "account_currency";
            this.reload();
        });
    },
    /**
     * Setup the account filter option.
     *
     * This options is displayed as a many2one-like search input.
     * The list of available accounts is rendered server-side with qweb.
     */
    setupAvailableAccountsOption(){
        this.$searchview_buttons.find(".o_account_reports_account_auto_complete").select2();
        var account = this.report_options.account;
        var select = this.$searchview_buttons.find(".o_account_reports_account_auto_complete").data().select2;
        if(account){
            select.onSelect({id: account[0], text: account[1]});
        }
        else{
            select.onSelect({id: null, text: ""});
        }

        this.$searchview_buttons.find(".o_account_reports_add_account").bind("click", (event) => {
            var data = this.$searchview_buttons.find(".o_account_reports_account_auto_complete").select2("data");
            this.report_options.account = data.id !== "-1" ? [data.id, data.text] : null;
            this.reload();
        });
    },
});

});
