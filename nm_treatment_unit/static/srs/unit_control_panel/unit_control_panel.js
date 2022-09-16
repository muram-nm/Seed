/** @odoo-module **/

import { ControlPanel } from "@web/search/control_panel/control_panel";
import { useService } from "@web/core/utils/hooks";

export class UnitControlPanel extends ControlPanel {
    constructor() {
        super(...arguments);
        this.orm = useService("orm");
        this.user = useService("user");
        const { active_id, show_unit_update } = this.env.searchModel.globalContext;
        this.showUnitUpdate = this.env.config.viewType === "form" || show_unit_update;
        this.unitId = this.showUnitUpdate ? active_id : false;
    }

    async willStart() {
        const proms = [super.willStart(...arguments)];
        if (this.showUnitUpdate) {
            proms.push(this.loadData());
        }
        await Promise.all(proms);
    }

    async willUpdateProps() {
        const proms = [super.willUpdateProps(...arguments)];
        if (this.showUnitUpdate) {
            proms.push(this.loadData());
        }
        await Promise.all(proms);
    }

    async loadData() {
        const [data, isUnitUser] = await Promise.all([
            this.orm.call("unit.unit", "get_last_update_or_default", [this.unitId]),
            this.user.hasGroup("nm_treatment_unit.group_unit_user"),
        ]);
        this.data = data;
        this.isUnitUser = isUnitUser;
    }

    async onStatusClick(ev) {
        ev.preventDefault();
        this.actionService.doAction("nm_treatment_unit.unit_update_all_action", {
            additionalContext: {
                default_project_id: this.unitId,
                active_id: this.unitId,
            },
        });
    }
}

UnitControlPanel.template = "nm_treatment_unit.UnitControlPanel";
