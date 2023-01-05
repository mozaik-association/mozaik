# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ChangeAddress(models.TransientModel):

    _inherit = "change.address"

    update_instance = fields.Boolean(default=True)

    def doit(self):
        res = super(ChangeAddress, self).doit()
        default_instance = self.env["int.instance"]._get_default_int_instance()
        for wizard in self:
            if wizard.update_instance:
                w = self.env["change.instance"].create(
                    {
                        "instance_id": wizard.address_id.city_id.int_instance_id.id
                        or default_instance.id,
                        "partner_ids": wizard.partner_ids.ids,
                    }
                )
                w.doit()
        return res
