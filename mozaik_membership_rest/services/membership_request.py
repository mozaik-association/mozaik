# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import collections
import logging

from odoo.exceptions import UserError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel
from odoo.addons.component.core import Component

from ..pydantic_models.membership_request import MembershipRequest
from ..pydantic_models.membership_request_info import MembershipRequestInfo

_logger = logging.getLogger(__name__)
trace = _logger.info


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
        return MembershipRequestInfo.from_orm(membership_request)

    @restapi.method(
        routes=[(["/membership_request"], "POST")],
        input_param=PydanticModel(MembershipRequest),
        output_param=PydanticModel(MembershipRequestInfo),
        auth="public",
    )
    def membership_request(
        self, membership_request: MembershipRequest
    ) -> MembershipRequestInfo:
        vals = membership_request.dict()

        if vals["distribution_list_ids_opt_out"]:
            dlists_optout = self.env["distribution.list"].search(
                [
                    ("code", "in", vals["distribution_list_ids_opt_out"]),
                    ("newsletter", "=", True),
                ]
            )
            if dlists_optout:
                vals["distribution_list_ids_opt_out"] = [(6, 0, dlists_optout.ids)]
            else:
                del vals["distribution_list_ids_opt_out"]
                _logger.info(
                    "Unknown distribution_list_ids with code %s",
                    vals["distribution_list_ids_opt_out"],
                )

        if vals["distribution_list_ids"]:
            dlists = self.env["distribution.list"].search(
                [
                    ("code", "in", vals["distribution_list_ids"]),
                    ("newsletter", "=", True),
                ]
            )
            if dlists:
                vals["distribution_list_ids"] = [(6, 0, dlists.ids)]
            else:
                del vals["distribution_list_ids"]
                _logger.info(
                    "Unknown distribution_list_ids with code %s",
                    vals["distribution_list_ids"],
                )
        if vals["involvement_category_ids"]:
            if not isinstance(vals["involvement_category_ids"], collections.Iterable):
                cats = self.env["partner.involvement.category"].search(
                    [("code", "in", vals["involvement_category_ids"])]
                )
            if cats:
                vals["involvement_category_ids"] = [(6, 0, cats.ids)]
            else:
                del vals["involvement_category_ids"]
                _logger.info(
                    "Unknown involvements with code %s",
                    vals["involvement_category_ids"],
                )
        if vals["nationality_id"]:
            nat = self.env["res.country"].search(
                [("code", "=", vals["nationality_id"])]
            )
            if nat:
                vals["nationality_id"] = nat.id
            else:
                del vals["nationality_id"]
                _logger.info("Unknown nationality with code %s", vals["nationality"])
        try:
            mr = self.env["membership.request"].with_context(autoval=True).create(vals)
            if membership_request.auto_validate:
                mr.validate_request()
        except Exception as e:
            raise UserError(
                self.env.user.id, "Membership Request", "CREATE ERROR", e.message
            ) from e

        return MembershipRequestInfo.from_orm(mr)
