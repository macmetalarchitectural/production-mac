/** @odoo-module **/
import { AttendeeCalendarCommonPopover } from "@calendar/views/attendee_calendar/common/attendee_calendar_common_popover";
import { patch } from "@web/core/utils/patch";
import { useState, onWillStart } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

patch(AttendeeCalendarCommonPopover.prototype, {
    setup() {
        super.setup(...arguments);
        // this.orm and this.actionService are already set by super.setup()
        this.macState = useState({ completed: false });

        onWillStart(async () => {
            if (this.props.record?.id) {
                const result = await this.orm.read(
                    "calendar.event",
                    [this.props.record.id],
                    ["completed"]
                );
                this.macState.completed =
                    result.length > 0 && result[0].completed === "yes";
            }
        });
    },

    async onClickDone() {
        await this.orm.call("calendar.event", "action_done", [
            [this.props.record.id],
        ]);
        await this.props.model.load();
        this.props.close();
    },

    async onClickDoneScheduleNext() {
        const partnerIds = this.props.record.rawRecord.partner_ids || [];
        await this.orm.call("calendar.event", "action_done", [
            [this.props.record.id],
        ]);
        this.props.close();
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: _t("Schedule activity"),
            res_model: "calendar.event",
            view_mode: "form",
            views: [[false, "form"]],
            target: "current",
            context: {
                default_partner_ids: partnerIds,
            },
            res_id: false,
        });
    },
});
