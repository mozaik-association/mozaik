# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel
from odoo.addons.component.core import Component
from odoo.addons.mozaik_membership_request_protected_values.models.membership_request import (
    VOLUNTARY_FIELD_NAMES,
)

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
    )
    def get(self, _id: int) -> MembershipRequestInfo:
        membership_request = self._get(_id)
        return MembershipRequestInfo.from_orm(membership_request)

    def _validate_country_city(self, vals):
        nat = self.env["res.country"].search([("id", "=", vals["country_id"])])
        if nat:
            vals["country_id"] = nat.id
            city = self.env["res.city"].browse()
            if "city_id" in vals:
                city = self.env["res.city"].search([("id", "=", vals["city_id"])])
            if nat.enforce_cities:
                if not city:
                    raise ValidationError(
                        _(
                            "City_id is mandatory on addresses "
                            "with 'enforce_cities' country"
                        )
                    )
                if city.country_id.id != vals["country_id"]:
                    raise ValidationError(
                        _("City_id's country must be equal to address' country")
                    )
        else:
            del vals["country_id"]
            _logger.info("Unknown nationality with id %s", vals["country_id"])
        return vals

    def _validate_involvement_category(self, vals):
        if not any(
            param in vals
            for param in ("involvement_category_ids", "involvement_category_codes")
        ):
            return vals
        cats = self.env["partner.involvement.category"].browse()
        if vals["involvement_category_ids"]:
            cats |= self.env["partner.involvement.category"].search(
                [("id", "in", vals["involvement_category_ids"])]
            )
        if vals["involvement_category_codes"]:
            cats |= self.env["partner.involvement.category"].search(
                [("code", "in", vals["involvement_category_codes"])]
            )
        vals.pop("involvement_category_codes")
        vals["involvement_category_ids"] = [(6, 0, cats.ids)]
        return vals

    def _validate_voluntaries(self, vals):
        """
        local_voluntary, regional_voluntary, national_voluntary
        and local_only are selection fields.
        If the given string is something else than "force_true"
        or "force_false", we keep the field empty
        """
        for field_name in VOLUNTARY_FIELD_NAMES:
            value = vals.pop(field_name, False)
            if value in ["force_true", "force_false"]:
                vals[field_name] = value
            else:
                vals[field_name] = False
        return vals

    def _manage_distribution_list_ids(self, vals, key):
        if vals[key]:
            dlists = self.env["distribution.list"].search(
                [
                    ("id", "in", vals[key]),
                    ("newsletter", "=", True),
                ]
            )
            if dlists:
                vals[key] = [(6, 0, dlists.ids)]
            else:
                del vals[key]
                _logger.info(
                    "Unknown distribution_list_ids with id %s",
                    vals[key],
                )
        return vals

    def _validate_membership_request_input(self, input_data):
        vals = input_data.dict()
        vals = self._manage_distribution_list_ids(vals, "distribution_list_ids")
        vals = self._manage_distribution_list_ids(vals, "distribution_list_ids_opt_out")
        vals = self._validate_involvement_category(vals)
        vals = self._validate_voluntaries(vals)
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
            vals = self._validate_country_city(vals)
        del vals["auto_validate"]
        if not vals["partner_id"]:
            vals["partner_id"] = self.env.context.get("authenticated_partner_id", False)
        vals["force_autoval"] = vals.pop("force_auto_validate", False)
        vals["street_man"] = vals.pop("street", False)
        vals["zip_man"] = vals.pop("zip", False)
        vals["city_man"] = vals.pop("city", False)
        if vals.pop("auto_generate_reference", False):
            vals["reference"] = self.env[
                "membership.line"
            ]._generate_membership_reference(
                self.env["res.partner"].browse(vals["partner_id"]),
                self.env["int.instance"].browse(),
            )
        return vals

    def _get_protected_values(self, vals):
        """
        Always protect following values:
        * local_voluntary, regional_voluntary, national_voluntary
        * local_only
        * interests and competencies (that are already encoded as (6, 0, [ids]))
        """
        protected_values = {}
        for field_name in VOLUNTARY_FIELD_NAMES:
            protected_values[field_name] = vals.get(field_name, False)
        for field_name in ["interest_ids", "competency_ids"]:
            field_value = vals.get(field_name, False)
            if field_value:
                protected_values[field_name] = field_value[0][2]
        return protected_values

    def _create_membership_request_attachments(self, mr, attachments):
        for attachment in attachments:
            self.env["ir.attachment"].sudo().create(
                {
                    "name": attachment["name"],
                    "type": "binary",
                    "mimetype": attachment["mimetype"],
                    "datas": attachment["content"],
                    "res_model": "membership.request",
                    "res_id": mr.id,
                }
            )

    def _create_membership_request(self, membership_request):
        vals = self._validate_membership_request_input(membership_request)
        protected_values = self._get_protected_values(vals)
        vals["protected_values"] = protected_values
        # Check if an error will be raised because of the reference
        if "reference" in vals and vals["reference"]:
            error = self.env["membership.request"]._raise_error_check_reference(
                0, vals.get("reference", ""), vals.get("partner_id", False)
            )
            if error:
                return error
        mr = (
            self.env["membership.request"]
            .with_context(mode="pre_process", protected_values=protected_values)
            .create(vals)
        )
        attachments = membership_request.dict().get("attachments", False)
        if attachments:
            self._create_membership_request_attachments(mr, attachments)
        # We validate the request if asked, and force auto-validation if asked
        mr._auto_validate_may_be_forced(membership_request.auto_validate)
        return mr

    @restapi.method(
        routes=[(["/membership_request"], "POST")],
        input_param=PydanticModel(MembershipRequest),
        output_param=PydanticModel(MembershipRequestInfo),
    )
    def membership_request(
        self, membership_request: MembershipRequest
    ) -> MembershipRequestInfo:
        mr = self._create_membership_request(membership_request)
        if isinstance(mr, str):
            #  We got an error from the reference check
            return MembershipRequestInfo(bad_request_error=mr)
        return MembershipRequestInfo.from_orm(mr)
