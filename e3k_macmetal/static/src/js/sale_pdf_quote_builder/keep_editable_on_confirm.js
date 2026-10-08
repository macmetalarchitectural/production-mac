/** @odoo-module **/

import { useEffect, useState } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import {
    CustomContentKanbanLikeWidget,
} from "@sale_pdf_quote_builder/js/custom_content_kanban_like_widget/custom_content_kanban_like_widget";

patch(CustomContentKanbanLikeWidget.prototype, {
    /**
     * Native `setup()` registers a `useEffect` that mutates `this.props.readonly` to `true`
     * once the order reaches the 'sale' state, greying out the Quote Builder tab. A single
     * `useEffect` cannot be cancelled after registration, so `setup()` is reimplemented here
     * without that effect; everything else is kept identical to native so the selected
     * headers/footers/product documents stay selectable (and therefore printable) once the
     * order is confirmed.
     */
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            headers: {},
            lines: {},
            footers: {},
        });

        useEffect((saleOrderTemplate) => {
            this.updateState();
        }, () => [this.props.record.data.sale_order_template_id]);
    },
});
