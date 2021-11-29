# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class EventService(Component):
    _inherit = "event.rest.service"

    def _get_search_domain(self, filters):
        domain = super()._get_search_domain(filters)
        if filters.is_private:
            domain.append(("is_private", "=", filters.is_private))
        if filters.website_domain_ids:
            domain.append(("website_domain_ids", "in", filters.website_domain_ids))
        if filters.interest_ids:
            domain.append(("interest_ids", "in", filters.interest_ids))
        return domain
