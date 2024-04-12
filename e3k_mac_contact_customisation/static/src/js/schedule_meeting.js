/** @odoo-module **/

import { registerInstancePatchModel } from "@mail/model/model_core";

registerInstancePatchModel("mail.chatter", "voip/static/src/models/chatter/chatter.js", {

    /**
     * @override
     */
    _created() {
        const res = this._super(...arguments);
        this.onClickScheduleMeeting = this.onClickScheduleMeeting.bind(this);

    },

     onClickScheduleMeeting(ev) {
     console.log("onClickScheduleMeeting");
     console.log(this);

            const action = {
                type: 'ir.actions.act_window',
                name: this.env._t("Schedule activity"),
                res_model: 'calendar.event',
                view_mode: 'form',
                views: [[false, 'form']],
                target: 'current',
                context: {
                    default_res_id: this.thread.id,
                    default_res_model: this.thread.model,
                    default_partner_ids: [this.thread.id],

                },
                res_id: false,
            };
            return this.env.bus.trigger('do-action', {
                action,
                options: {
                    on_close: () => {
                        if (!this.componentChatterTopbar) {
                            return;
                        }
                        this.componentChatterTopbar.trigger('reload', { keepChanges: true });
                    },
                },
            });
        }

});
