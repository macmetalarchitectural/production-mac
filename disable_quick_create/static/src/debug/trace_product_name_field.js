/** @odoo-module **/

import { ProductLabelSectionAndNoteField } from "@account/components/product_label_section_and_note_field/product_label_section_and_note_field";
import { patch } from "@web/core/utils/patch";
import { traceLifecycle, traceGetters } from "./trace_lifecycle";

/**
 * Patch pour tracer le cycle de vie de ProductLabelSectionAndNoteField
 */
patch(ProductLabelSectionAndNoteField.prototype, traceLifecycle("ProductLabelSectionAndNoteField", {
    traceProps: true,
    specificProps: ["name", "canQuickCreate", "canCreateEdit", "record"],
    traceGetters: true,
    specificGetters: ["many2OneProps"]
}));

/**
 * Tracer le getter many2OneProps avec plus de détails
 */
const originalMany2OnePropsDescriptor = Object.getOwnPropertyDescriptor(
    ProductLabelSectionAndNoteField.prototype,
    'many2OneProps'
);

if (originalMany2OnePropsDescriptor?.get) {
    const originalGetter = originalMany2OnePropsDescriptor.get;

    Object.defineProperty(ProductLabelSectionAndNoteField.prototype, 'many2OneProps', {
        get() {
            console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
            console.log(`📦 [ProductLabelSectionAndNoteField] GET many2OneProps`);
            console.log(`   Appelé depuis:`, new Error().stack.split('\n')[2]);

            const props = originalGetter.call(this);

            console.log(`   Props retournées par super.many2OneProps:`);
            console.log(`     canQuickCreate:`, props.canQuickCreate);
            console.log(`     canCreateEdit:`, props.canCreateEdit);
            console.log(`     Toutes les props:`, props);

            const relation = this.props.record?.fields[this.props.name]?.relation;
            console.log(`   Relation du champ:`, relation);

            if (this.disableCreateEditService) {
                const isDisabled = this.disableCreateEditService.isDisabledSync(relation);
                console.log(`   Service disableCreateEdit:`, {
                    exists: !!this.disableCreateEditService,
                    isDisabled: isDisabled,
                    cached: isDisabled !== null
                });

                if (isDisabled) {
                    console.log(`   🔒 MODIFICATION DES PROPS DÉTECTÉE`);
                    console.log(`     Avant: canQuickCreate=${props.canQuickCreate}, canCreateEdit=${props.canCreateEdit}`);
                    props.canQuickCreate = false;
                    props.canCreateEdit = false;
                    console.log(`     Après: canQuickCreate=${props.canQuickCreate}, canCreateEdit=${props.canCreateEdit}`);
                }
            } else {
                console.log(`   ⚠️  Service disableCreateEdit non disponible`);
            }

            console.log(`   Props finales retournées:`, props);
            return props;
        }
    });
}

console.log("✓ Traçage du cycle de vie de ProductLabelSectionAndNoteField activé");
