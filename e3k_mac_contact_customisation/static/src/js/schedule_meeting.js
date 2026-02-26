/** @odoo-module **/
import { Chatter } from "@mail/chatter/web_portal/chatter";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

patch(Chatter.prototype, {
    setup() {
        super.setup(...arguments);
        this.macActionService = useService("action");
    },

    onClickScheduleMeeting() {
        const thread = this.state.thread;
        if (!thread?.id) {
            return;
        }
        this.macActionService.doAction(
            {
                type: "ir.actions.act_window",
                name: _t("Schedule activity"),
                res_model: "calendar.event",
                view_mode: "form",
                views: [[false, "form"]],
                target: "current",
                context: {
                    default_res_id: thread.id,
                    default_res_model: thread.model,
                    default_partner_ids: [thread.id],
                },
                res_id: false,
            },
            {
                onClose: () => {
                    if (this.state.thread) {
                        this.load(this.state.thread, ["activities", "messages"]);
                    }
                },
            }
        );
    },
});
