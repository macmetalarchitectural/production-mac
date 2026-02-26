/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

// ─── FilterCheckboxGroup ──────────────────────────────────────────────────────
// Composant générique : panel collapsible avec liste de checkboxes + "Select all"

class FilterCheckboxGroup extends Component {
    static template = "e3k_mac_contact_customisation.FilterCheckboxGroup";
    static props = {
        label: String,
        // filterKey doit correspondre à la clé dans state.filters ET state.openSections
        filterKey: String,
        items: Array,
        selectedIds: Array,
        isOpen: Boolean,
        onToggleSection: Function,
        onSelectAll: Function,   // (filterKey, allIds) => void
        onItemChange: Function,  // (filterKey, itemId) => void
    };

    get allSelected() {
        const { items, selectedIds } = this.props;
        return items.length > 0 && selectedIds.length === items.length;
    }
}

// ─── ActivityTable ────────────────────────────────────────────────────────────
// Composant dédié au tableau de résultats avec gestion du chargement

class ActivityTable extends Component {
    static template = "e3k_mac_contact_customisation.ActivityTable";
    static props = {
        rows: Array,
        isLoading: Boolean,
    };

    completedLabel(completed) {
        return completed === "yes" ? _t("Yes") : _t("No");
    }
}

// ─── ActivityDashboard ────────────────────────────────────────────────────────
// Composant root : gère l'état global et orchestre les sous-composants

export class ActivityDashboard extends Component {
    static template = "e3k_mac_contact_customisation.ActivityDashboard";
    static props = ["*"];
    static components = { FilterCheckboxGroup, ActivityTable };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            teams: [],
            reps: [],
            meetingTypes: [],
            statuses: [],
            periods: [],
            activityDetails: [],
            isLoading: false,
            filters: {
                teams: [],
                reps: [],
                meetingTypes: [],
                completed: [],
                status: [],
                fromDate: "",
                toDate: "",
                period: "",
            },
            // Les clés correspondent exactement aux clés de filters pour simplifier toggleSection
            openSections: {
                teams: false,
                reps: false,
                meetingTypes: false,
                status: false,
                completed: false,
            },
        });

        onWillStart(() => this._loadInitialData());
    }

    // Getter : items statiques pour le filtre "Closed"
    get completedItems() {
        return [
            { id: "yes", name: _t("Yes") },
            { id: "no", name: _t("No") },
        ];
    }

    // ── Chargement des données ───────────────────────────────────────────────

    async _loadInitialData() {
        const [teams, reps, meetingTypes, statuses, periods, details] =
            await Promise.all([
                this.orm.call("calendar.event", "get_teams", []),
                this.orm.call("calendar.event", "get_rep", []),
                this.orm.call("calendar.event", "get_meeting_type", []),
                this.orm.call("calendar.event", "get_status", []),
                this.orm.call("calendar.event", "get_period", []),
                this.orm.call("calendar.event", "get_activity_details", []),
            ]);
        Object.assign(this.state, {
            teams,
            reps,
            meetingTypes,
            statuses,
            periods,
            activityDetails: details,
        });
    }

    async _loadFilteredDetails() {
        this.state.isLoading = true;
        try {
            const f = this.state.filters;
            const details = await this.orm.call(
                "calendar.event",
                "get_activity_details_by_filter",
                [f.teams, f.reps, f.meetingTypes, f.completed, f.status, [f.fromDate, f.toDate], f.period]
            );
            this.state.activityDetails = details;
        } finally {
            this.state.isLoading = false;
        }
    }

    // ── Helpers ──────────────────────────────────────────────────────────────

    _toggleInList(list, value) {
        const idx = list.indexOf(value);
        if (idx >= 0) list.splice(idx, 1);
        else list.push(value);
    }

    async _updateRepsAndReload() {
        const teamIds = this.state.filters.teams;
        const method = teamIds.length ? "get_rep_by_team" : "get_rep";
        const args = teamIds.length ? [teamIds] : [];
        this.state.reps = await this.orm.call("calendar.event", method, args);
        this.state.filters.reps = [];
        await this._loadFilteredDetails();
    }

    // ── Handlers partagés avec FilterCheckboxGroup ───────────────────────────

    toggleSection(filterKey) {
        this.state.openSections[filterKey] = !this.state.openSections[filterKey];
    }

    // Handler générique toggle : met à jour le filtre et recharge
    async onFilterItemChange(filterKey, itemId) {
        this._toggleInList(this.state.filters[filterKey], itemId);
        await this._loadFilteredDetails();
    }

    // Handler générique "select all" : bascule tout ou rien
    async onFilterSelectAll(filterKey, allIds) {
        const f = this.state.filters;
        f[filterKey] = f[filterKey].length === allIds.length ? [] : [...allIds];
        await this._loadFilteredDetails();
    }

    // Handler spécifique teams : recharge aussi la liste des reps
    async onTeamItemChange(filterKey, teamId) {
        this._toggleInList(this.state.filters.teams, teamId);
        await this._updateRepsAndReload();
    }

    async onTeamSelectAll(filterKey, allIds) {
        const f = this.state.filters;
        f.teams = f.teams.length === allIds.length ? [] : [...allIds];
        await this._updateRepsAndReload();
    }

    // ── Handlers période / dates ─────────────────────────────────────────────

    async onPeriodChange(ev) {
        this.state.filters.period = ev.target.value;
        if (this.state.filters.period) {
            this.state.filters.fromDate = "";
            this.state.filters.toDate = "";
        }
        await this._loadFilteredDetails();
    }

    async onDateChange(field, ev) {
        this.state.filters[field] = ev.target.value;
        if (this.state.filters[field]) {
            this.state.filters.period = "";
        }
        await this._loadFilteredDetails();
    }
}

registry.category("actions").add("activity_dashboard", ActivityDashboard);
