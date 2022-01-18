# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.membership_request import (
    MembershipRequest,
)
from ..pydantic_models.membership_request_info import (
    MembershipRequestInfo,
)
class MembershipRequestService(Component):
    _inherit = "base.membership.rest.service"
    _name = "membership.request.rest.service"
    _usage = "membership_request"
    _expose_model = "membership.request"
    _description = __doc__

    @restapi.method(
            routes=[(["/<int:_id>"], "GET")],
            output_param=PydanticModel(MembershipRequestInfo),
            auth="public",
    )
    def get(self, _id: int) -> MembershipRequestInfo:
      membership_request = self._get(_id)
      return MemblocalhershipRequestInfo.from_orm(membership_request)


    @restapi.method(
        routes=[(["/membership_request/<int:autovalidate>"], "POST")],
        input_param=PydanticModel(MembershipRequest),
        output_param=PydanticModel(MembershipRequestInfo),
        auth="public",
    )
    def membership_request(
        self,
        autovalidate,
        membership_request: MembershipRequest
    ) -> MembershipRequestInfo:
        mr_obj = self.env["membership.request"]
        vals = membership_request.dict()
        mr = mr_obj.with_context(autoval=True).create(vals)
        if(autovalidate):
            mr.validate_request()

        return MembershipRequestInfo.from_orm(mr)
