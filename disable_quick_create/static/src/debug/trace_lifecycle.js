/** @odoo-module **/

import { onWillStart, onMounted, onWillUpdateProps, onWillPatch, onPatched, onWillUnmount, onWillDestroy } from "@odoo/owl";

/**
 * CYCLE DE VIE D'UN COMPOSANT OWL (dans l'ordre chronologique) :
 *
 * 1. constructor() - Création de l'instance
 * 2. setup() - Configuration du composant (hooks, services, etc.)
 * 3. onWillStart - Avant le premier rendu (async possible)
 * 4. Premier rendu (template)
 * 5. onMounted - Après insertion dans le DOM
 *
 * Lors d'une mise à jour :
 * 6. onWillUpdateProps - Avant mise à jour des props (async possible)
 * 7. onWillPatch - Avant patch du DOM
 * 8. Re-rendu (template)
 * 9. onPatched - Après patch du DOM
 *
 * Lors de la destruction :
 * 10. onWillUnmount - Avant retrait du DOM
 * 11. onWillDestroy - Avant destruction complète
 */

/**
 * Mixin pour tracer le cycle de vie complet d'un composant OWL
 * @param {string} componentName - Nom du composant pour les logs
 * @param {Object} options - Options de configuration
 * @param {boolean} options.traceProps - Tracer toutes les props (défaut: true)
 * @param {Array<string>} options.specificProps - Liste de props spécifiques à tracer
 * @param {boolean} options.traceGetters - Tracer les getters (défaut: false)
 * @param {Array<string>} options.specificGetters - Liste de getters spécifiques à tracer
 */
export function traceLifecycle(componentName = "Component", options = {}) {
    const {
        traceProps = true,
        specificProps = [],
        traceGetters = false,
        specificGetters = []
    } = options;

    return {
        setup() {
            console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
            console.log(`🔷 [${componentName}] SETUP - Configuration du composant`);
            this._logProps("Props initiales");

            // Tracer onWillStart
            onWillStart(async () => {
                console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
                console.log(`🔵 [${componentName}] ON_WILL_START - Avant premier rendu`);
                this._logProps("Props dans onWillStart");
            });

            // Tracer onMounted
            onMounted(() => {
                console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
                console.log(`🟢 [${componentName}] ON_MOUNTED - Composant monté dans le DOM`);
                this._logProps("Props dans onMounted");
                console.log(`   DOM Element:`, this.el);
            });

            // Tracer onWillUpdateProps
            onWillUpdateProps((nextProps) => {
                console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
                console.log(`🟡 [${componentName}] ON_WILL_UPDATE_PROPS - Props vont changer`);
                this._logPropsComparison(this.props, nextProps);
            });

            // Tracer onWillPatch
            onWillPatch(() => {
                console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
                console.log(`🟠 [${componentName}] ON_WILL_PATCH - Avant patch du DOM`);
                this._logProps("Props dans onWillPatch");
            });

            // Tracer onPatched
            onPatched(() => {
                console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
                console.log(`🟣 [${componentName}] ON_PATCHED - DOM patché`);
                this._logProps("Props dans onPatched");
            });

            // Tracer onWillUnmount
            onWillUnmount(() => {
                console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
                console.log(`🔴 [${componentName}] ON_WILL_UNMOUNT - Avant retrait du DOM`);
                this._logProps("Props finales");
            });

            // Tracer onWillDestroy
            onWillDestroy(() => {
                console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
                console.log(`⚫ [${componentName}] ON_WILL_DESTROY - Destruction du composant`);
            });

            // Appeler super.setup si c'est un patch
            if (super.setup) {
                super.setup(...arguments);
            }
        },

        /**
         * Helper pour logger les props
         */
        _logProps(label = "Props") {
            console.log(`   ${label}:`);

            if (traceProps && specificProps.length === 0) {
                // Tracer toutes les props
                console.log(`     Toutes les props:`, this.props);
            } else if (specificProps.length > 0) {
                // Tracer uniquement les props spécifiques
                specificProps.forEach(propName => {
                    console.log(`     ${propName}:`, this.props[propName]);
                });
            }

            // Tracer des props communes utiles
            if (this.props.name) console.log(`     name:`, this.props.name);
            if (this.props.record) console.log(`     record.resModel:`, this.props.record.resModel);
            if (this.props.canQuickCreate !== undefined) console.log(`     canQuickCreate:`, this.props.canQuickCreate);
            if (this.props.canCreateEdit !== undefined) console.log(`     canCreateEdit:`, this.props.canCreateEdit);
        },

        /**
         * Helper pour comparer les props actuelles et nouvelles
         */
        _logPropsComparison(oldProps, newProps) {
            console.log(`   Comparaison des props:`);

            const propsToCompare = specificProps.length > 0
                ? specificProps
                : [...new Set([...Object.keys(oldProps), ...Object.keys(newProps)])];

            let hasChanges = false;
            propsToCompare.forEach(key => {
                if (oldProps[key] !== newProps[key]) {
                    hasChanges = true;
                    console.log(`     ✏️  ${key}:`, {
                        old: oldProps[key],
                        new: newProps[key]
                    });
                }
            });

            if (!hasChanges) {
                console.log(`     ✓ Aucune différence détectée`);
            }
        },

        /**
         * Helper pour obtenir les différences entre deux objets
         */
        _getDiff(oldProps, newProps) {
            const diff = {};
            const allKeys = new Set([...Object.keys(oldProps), ...Object.keys(newProps)]);

            for (const key of allKeys) {
                if (oldProps[key] !== newProps[key]) {
                    diff[key] = {
                        old: oldProps[key],
                        new: newProps[key]
                    };
                }
            }

            return Object.keys(diff).length > 0 ? diff : null;
        }
    };
}

/**
 * Helper pour tracer les getters d'un composant
 * @param {Object} component - Le prototype du composant
 * @param {string} componentName - Nom du composant
 * @param {Array<string>} getterNames - Liste des getters à tracer
 */
export function traceGetters(component, componentName, getterNames) {
    getterNames.forEach(getterName => {
        const originalGetter = Object.getOwnPropertyDescriptor(component, getterName)?.get;

        if (!originalGetter) {
            console.warn(`Getter ${getterName} not found on ${componentName}`);
            return;
        }

        Object.defineProperty(component, getterName, {
            get() {
                console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
                console.log(`📦 [${componentName}] GET ${getterName}`);

                const result = originalGetter.call(this);

                console.log(`   Valeur retournée:`, result);
                console.log(`   Props actuelles:`, this.props);

                return result;
            }
        });
    });
}
