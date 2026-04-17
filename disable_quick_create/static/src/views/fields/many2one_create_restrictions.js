/** @odoo-module **/

import { Many2One } from "@web/views/fields/many2one/many2one";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onWillUpdateProps } from "@odoo/owl";

/**
 * Service pour gérer les configurations des modèles avec disable_create_edit
 */
export const disableCreateEditService = {
    dependencies: ["orm"],

    start(env, { orm }) {
        const modelsConfig = {};

        return {
            /**
             * Vérifie si un modèle a disable_create_edit activé
             * @param {string} resModel - Le nom du modèle
             * @returns {Promise<boolean>}
             */
            async isDisabled(resModel) {
                if (!resModel) return false;

                // Cache des résultats pour éviter les appels répétitifs
                if (resModel in modelsConfig) {
                    return modelsConfig[resModel];
                }

                try {
                    const result = await orm.searchRead(
                        "ir.model",
                        [["model", "=", resModel]],
                        ["disable_create_edit"],
                        { limit: 1 }
                    );

                    modelsConfig[resModel] = result.length > 0 && result[0].disable_create_edit;
                    return modelsConfig[resModel];
                } catch (error) {
                    console.error(`Error checking disable_create_edit for model ${resModel}:`, error);
                    modelsConfig[resModel] = false;
                    return false;
                }
            },

            /**
             * Vérifie de manière synchrone si un modèle a disable_create_edit activé (depuis le cache)
             * @param {string} resModel - Le nom du modèle
             * @returns {boolean|null} - true/false si en cache, null sinon
             */
            isDisabledSync(resModel) {
                if (!resModel) return false;
                return resModel in modelsConfig ? modelsConfig[resModel] : null;
            },

            /**
             * Réinitialise le cache pour un modèle spécifique ou tous les modèles
             * @param {string|null} resModel - Le nom du modèle ou null pour tous
             */
            clearCache(resModel = null) {
                if (resModel) {
                    delete modelsConfig[resModel];
                } else {
                    Object.keys(modelsConfig).forEach(key => delete modelsConfig[key]);
                }
            }
        };
    }
};

registry.category("services").add("disableCreateEdit", disableCreateEditService);

/**
 * Patch du composant Many2One (la classe de base)
 * Tous les champs Many2One héritent de cette classe :
 * - Many2OneField
 * - ProductNameAndDescriptionField
 * - ProductLabelSectionAndNoteField
 * - SaleOrderLineProductField
 * - etc.
 *
 * En patchant Many2One.prototype, on intercepte TOUS les champs Many2One automatiquement
 */
patch(Many2One.prototype, {
    setup() {
        super.setup(...arguments);
        this.disableCreateEditService = useService("disableCreateEdit");
        this._applyDisableCreateEdit();

        // Intercepter et modifier les props AVANT qu'elles ne soient appliquées lors des mises à jour
        onWillUpdateProps(async (nextProps) => {
            if (nextProps.relation) {
                const relation = nextProps.relation;
                if (relation && this.disableCreateEditService) {
                    const isDisabled = await this.disableCreateEditService.isDisabled(relation);

                    if (isDisabled) {
                        // Modifier directement nextProps AVANT qu'elles ne soient appliquées
                        nextProps.canQuickCreate = false;
                        nextProps.canCreateEdit = false;
                    }
                }
            }
        });
    },

    async _applyDisableCreateEdit() {
        const relation = this.props.relation;

        if (!relation) return;

        try {
            const isDisabled = await this.disableCreateEditService.isDisabled(relation);
            if (isDisabled) {
                // Désactiver uniquement quick create et create and edit
                this.props.canQuickCreate = false;
                this.props.canCreateEdit = false;

                // Forcer le re-render
                if (this.__owl__) {
                    this.render();
                }
            }
        } catch (error) {
            console.error(`Error applying disable_create_edit for ${relation}:`, error);
        }
    }
});
