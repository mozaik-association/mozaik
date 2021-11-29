# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class EventStageService(Component):
    _inherit = "event.stage.rest.service"

    def _get_search_domain(self, filters):
        domain = super()._get_search_domain(filters)
        if filters.draft_stage is not None:
            domain.append(("draft_stage", "=", filters.draft_stage))
        return domain
