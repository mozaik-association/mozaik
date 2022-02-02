# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

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

    def _validate_membership_request_input(self, input_data):
        vals = input_data.dict()
        if vals["distribution_list_ids"]:
            dlists = self.env["distribution.list"].search(
                [
                    ("id", "in", vals["distribution_list_ids"]),
                    ("newsletter", "=", True),
                ]
            )
            if dlists:
                vals["distribution_list_ids"] = [(6, 0, dlists.ids)]
            else:
                del vals["distribution_list_ids"]
                _logger.info(
                    "Unknown distribution_list_ids with id %s",
                    vals["distribution_list_ids"],
                )
        if vals["involvement_category_ids"]:
            if vals["involvement_category_ids"]:
                cats = self.env["partner.involvement.category"].search(
                    [("id", "in", vals["involvement_category_ids"])]
                )
            if cats:
                vals["involvement_category_ids"] = [(6, 0, cats.ids)]
            else:
                del vals["involvement_category_ids"]
                _logger.info(
                    "Unknown involvements with id %s",
                    vals["involvement_category_ids"],
                )
        if vals["interest_ids"]:
            if vals["interest_ids"]:
                cats = self.env["thesaurus.term"].search(
                    [("id", "in", vals["interest_ids"])]
                )
            if cats:
                vals["interest_ids"] = [(6, 0, cats.ids)]
            else:
                del vals["interest_ids"]
                _logger.info(
                    "Unknown interest with id %s",
                    vals["interest_ids"],
                )
        if vals["competency_ids"]:
            if vals["competency_ids"]:
                cats = self.env["thesaurus.term"].search(
                    [("id", "in", vals["competency_ids"])]
                )
            if cats:
                vals["competency_ids"] = [(6, 0, cats.ids)]
            else:
                del vals["competency_ids"]
                _logger.info(
                    "Unknown competency with id %s",
                    vals["competency_ids"],
                )
        if vals["nationality_id"]:
            nat = self.env["res.country"].search([("id", "=", vals["nationality_id"])])
            if nat:
                vals["nationality_id"] = nat.id
            else:
                del vals["nationality_id"]
                _logger.info("Unknown nationality with id %s", vals["nationality_id"])
        if vals["country_id"]:
            nat = self.env["res.country"].search([("id", "=", vals["country_id"])])
            if nat:
                vals["country_id"] = nat.id
            else:
                del vals["country_id"]
                _logger.info("Unknown nationality with id %s", vals["country_id"])
        del vals["auto_validate"]
        return vals

    @restapi.method(
        routes=[(["/membership_request"], "POST")],
        input_param=PydanticModel(MembershipRequest),
        output_param=PydanticModel(MembershipRequestInfo),
        auth="public",
    )
    def membership_request(
        self, membership_request: MembershipRequest
    ) -> MembershipRequestInfo:
        vals = self._validate_membership_request_input(membership_request)
        mr = self.env["membership.request"].create(vals)
        if membership_request.auto_validate:
            mr.validate_request()

        return MembershipRequestInfo.from_orm(mr)
