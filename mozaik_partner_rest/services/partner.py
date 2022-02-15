# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class PartnerService(Component):
    _inherit = "partner.rest.service"

    def _prepare_update_values(self, values, partner):
        res = super()._prepare_update_values(values, partner)
        if "subordinate_ids" in res:
            res["subordinate_ids"] = [(6, 0, res["subordinate_ids"])]
        if "partner_involvement_ids" in res:
            res["partner_involvement_ids"] = [(6, 0, res["partner_involvement_ids"])]
        if any(
            address_field in res
            for address_field in [
                "street",
                "street2",
                "number",
                "box",
                "city_id",
                "country_id",
            ]
        ):
            street = street2 = number = box = country_id = city_id = False
            partner_address = partner.address_address_id
            if partner_address:
                street = partner_address.street_man
                street2 = partner_address.street2
                number = partner_address.number
                box = partner_address.box
                country_id = partner_address.country_id.id
                if partner_address.city_id:
                    city_id = partner_address.city_id.id
            if "street" in res:
                street = res.pop("street")
            if "street2" in res:
                street2 = res.pop("street2")
            if "number" in res:
                number = res.pop("number")
            if "box" in res:
                box = res.pop("box")
            if "city_id" in res:
                city_id = res.pop("city_id")
            if "country_id" in res:
                country_id = res.pop("country_id")
            address = self.env["address.address"].search(
                [
                    ("street_man", "=", street),
                    ("street2", "=", street2),
                    ("number", "=", number),
                    ("box", "=", box),
                    ("city_id", "=", city_id),
                    ("country_id", "=", country_id),
                ],
                limit=1,
            )
            if not address:
                address = self.env["address.address"].create(
                    {
                        "street_man": street,
                        "street2": street2,
                        "number": number,
                        "box": box,
                        "city_id": city_id,
                        "country_id": country_id,
                    }
                )
            res["address_address_id"] = address.id
        return res
