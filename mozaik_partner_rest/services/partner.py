# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# flake8: noqa

from collections import OrderedDict
from typing import List

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.partner_info import PartnerInfo, PartnerShortInfo
from ..pydantic_models.partner_info_update import PartnerInfoUpdate
from ..pydantic_models.partner_search_filter import PartnerSearchFilter


class PartnerService(Component):
    _inherit = "base.partner.rest.service"
    _name = "partner.rest.service"
    _usage = "partner"
    _expose_model = "res.partner"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")], output_param=PydanticModel(PartnerInfo)
    )
    def get(self, _id: int) -> PartnerInfo:
        partner = self._get(_id)
        return PartnerInfo.from_orm(partner)

    def _get_search_domain(self, filters):
        domain = []
        if filters.name:
            domain.append(("name", "like", filters.name))
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.ref:
            domain.append(("ref", "like", filters.ref))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(PartnerSearchFilter),
        output_param=PydanticModelList(PartnerShortInfo),
    )
    def search(
        self, partner_search_filter: PartnerSearchFilter
    ) -> List[PartnerShortInfo]:
        domain = self._get_search_domain(partner_search_filter)
        res: List[PartnerShortInfo] = []
        for e in self.env["res.partner"].sudo().search(domain):
            res.append(PartnerShortInfo.from_orm(e))
        return res

    def _prepare_address_fields(self, values, partner):
        street_man = (
            street2
        ) = number = box = zip_man = city_man = country_id = city_id = False
        partner_address = partner.address_address_id
        if partner_address:
            street_man = partner_address.street_man
            street2 = partner_address.street2
            number = partner_address.number
            box = partner_address.box
            zip_man = partner_address.zip_man
            city_man = partner_address.city_man
            country_id = partner_address.country_id.id
            if partner_address.city_id:
                city_id = partner_address.city_id.id
        if "street" in values:
            street_man = values.pop("street")
        if "street2" in values:
            street2 = values.pop("street2")
        if "number" in values:
            number = values.pop("number")
        if "box" in values:
            box = values.pop("box")
        if "zip" in values:
            zip_man = values.pop("zip")
        if "city" in values:
            city_man = values.pop("city")
        if "city_id" in values:
            city_id = values.pop("city_id")
        if "country_id" in values:
            country_id = values.pop("country_id")
        if not country_id:
            if any(
                field
                for field in [
                    street_man,
                    street2,
                    number,
                    box,
                    zip_man,
                    city_man,
                    city_id,
                ]
            ):
                raise ValidationError(_("Country is mandatory on addresses"))
            values["address_address_id"] = False
            return values
        country_enforce_cities = (
            self.env["res.country"].browse(country_id).enforce_cities
        )
        if country_enforce_cities:
            if not city_id:
                raise ValidationError(
                    _(
                        "City_id is mandatory on addresses "
                        "with 'enforce_cities' country"
                    )
                )
            if self.env["res.city"].browse(city_id).country_id.id != country_id:
                raise ValidationError(
                    _("City_id's country must be equal to address' country")
                )
            zip_man = city_man = False
        else:
            if not zip_man or not city_man:
                raise ValidationError(
                    _(
                        "zip and city are mandatory on addresses "
                        "without 'enforce_cities' country"
                    )
                )
            city_id = False
        technical_name = self.env["address.address"]._get_technical_name(
            OrderedDict(
                [
                    ("country_id", country_id),
                    ("city_id", city_id),
                    ("zip_man", zip_man),
                    ("city_man", city_man),
                    ("address_local_street_id", False),
                    ("street_man", street_man),
                    ("number", number),
                    ("box", box),
                ]
            )
        )
        address = self.env["address.address"].search(
            [("technical_name", "=", technical_name)], limit=1
        )
        if not address:
            address = self.env["address.address"].create(
                {
                    "street_man": street_man,
                    "street2": street2,
                    "number": number,
                    "box": box,
                    "zip_man": zip_man,
                    "city_man": city_man,
                    "city_id": city_id,
                    "country_id": country_id,
                }
            )
        values["address_address_id"] = address.id
        return values

    def _prepare_update_values(self, values, partner):
        res = super()._prepare_update_values(values, partner)
        if "subordinate_ids" in res:
            res["subordinate_ids"] = [(6, 0, res["subordinate_ids"])]
        if any(
            address_field in values
            for address_field in [
                "street",
                "street2",
                "number",
                "box",
                "zip",
                "city",
                "city_id",
                "country_id",
            ]
        ):
            res = self._prepare_address_fields(res, partner)
        if (
            res.pop("update_instance", False)
            and "address_address_id" in res
            and res["address_address_id"]
        ):
            self.env["change.instance"].create(
                {
                    "instance_id": self.env["address.address"]
                    .browse(res["address_address_id"])
                    .city_id.int_instance_id.id,
                    "partner_ids": [partner.id],
                }
            ).doit()
        return res

    @restapi.method(
        routes=[(["/<int:_id>/update"], "POST")],
        input_param=PydanticModel(PartnerInfoUpdate),
        output_param=PydanticModel(PartnerInfo),
    )
    def update(self, _id: int, partner_info_update: PartnerInfoUpdate) -> PartnerInfo:
        partner = self._get(_id)
        values = self._prepare_update_values(
            partner_info_update.dict(exclude_unset=True), partner
        )
        partner.write(values)
        return PartnerInfo.from_orm(partner)
