# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.membership_request_origin_info import MembershipRequestOriginInfo


class MembershipRequestOriginService(Component):
    _inherit = "base.membership.rest.service"
    _name = "membership.request.origin.rest.service"
    _usage = "membership_request_origin"
    _expose_model = "membership.request.origin"
    _description = __doc__

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        output_param=PydanticModelList(MembershipRequestOriginInfo),
    )
    def search(self) -> List[MembershipRequestOriginInfo]:
        res: List[MembershipRequestOriginInfo] = []
        for rec in self.env["membership.request.origin"].sudo().search([]):
            res.append(MembershipRequestOriginInfo.from_orm(rec))
        return res
