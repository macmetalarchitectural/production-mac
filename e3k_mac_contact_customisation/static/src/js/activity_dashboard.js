/** @odoo-module **/
import { Component, useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
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
// Composant dédié au tableau de résultats avec pagination côté client.
// pageSize === 0 signifie "Tout afficher".

const PAGE_SIZES = [25, 50, 100, 0];   // 0 = Tout
const DEFAULT_PAGE_SIZE = 50;

class ActivityTable extends Component {
    static template = "e3k_mac_contact_customisation.ActivityTable";
    static props = {
        rows: Array,
        isLoading: Boolean,
    };

    setup() {
        this.pageSizes = PAGE_SIZES;
        this.state = useState({
            currentPage: 1,
            pageSize: DEFAULT_PAGE_SIZE,
        });
        // Réinitialise la page quand les données changent (nouveau filtre)
        onWillUpdateProps(() => {
            this.state.currentPage = 1;
        });
    }

    // ── Getters pagination ────────────────────────────────────────────────────

    get showAll() {
        return this.state.pageSize === 0;
    }

    get totalPages() {
        if (this.showAll) return 1;
        return Math.max(1, Math.ceil(this.props.rows.length / this.state.pageSize));
    }

    get pagedRows() {
        if (this.showAll) return this.props.rows;
        const start = (this.state.currentPage - 1) * this.state.pageSize;
        return this.props.rows.slice(start, start + this.state.pageSize);
    }

    get fromRow() {
        if (this.props.rows.length === 0) return 0;
        if (this.showAll) return 1;
        return (this.state.currentPage - 1) * this.state.pageSize + 1;
    }

    get toRow() {
        if (this.showAll) return this.props.rows.length;
        return Math.min(this.state.currentPage * this.state.pageSize, this.props.rows.length);
    }

    // Génère la liste des numéros de page avec ellipses : [1, '...', 4, 5, 6, '...', 12]
    get pageNumbers() {
        const total = this.totalPages;
        const current = this.state.currentPage;
        if (total <= 7) {
            return Array.from({ length: total }, (_, i) => i + 1);
        }
        const range = new Set([1, total]);
        for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
            range.add(i);
        }
        const sorted = [...range].sort((a, b) => a - b);
        const pages = [];
        let prev = 0;
        for (const p of sorted) {
            if (p - prev > 1) pages.push("...");
            pages.push(p);
            prev = p;
        }
        return pages;
    }

    // ── Handlers pagination ───────────────────────────────────────────────────

    goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.state.currentPage = page;
        }
    }

    onPageSizeChange(ev) {
        this.state.pageSize = parseInt(ev.target.value, 10);
        this.state.currentPage = 1;
    }

    // ── Helpers ──────────────────────────────────────────────────────────────

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
