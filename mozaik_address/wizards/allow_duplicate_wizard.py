# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
from odoo.fields import first


class AllowDuplicateWizard(models.TransientModel):

    _inherit = "allow.duplicate.wizard"
    _name = "allow.duplicate.address.wizard"

    address_id = fields.Many2one(
        "address.address", string="Co-Residency", readonly=True
    )
    co_residency_id = fields.Many2one(
        "co.residency", string="Co-Residency", readonly=True
    )

    @api.model
    def default_get(self, fields_list):
        """
        To get default values for the object.
        """
        res = super().default_get(fields_list)
        if "address_id" in fields_list or "co_residency_id" in fields_list:
            ids = (
                self.env.context.get("active_id")
                and [self.env.context.get("active_id")]
                or self.env.context.get("active_ids")
                or []
            )
            for coord in self.env["postal.coordinate"].browse(ids):
                address = coord.address_id
                res["address_id"] = address.id
                cor_ids = self.env["co.residency"].search(
                    [("address_id", "=", address.id)]
                )
                if cor_ids:
                    res["co_residency_id"] = first(cor_ids).id
                break

        return res

    def button_allow_duplicate(self):
        """
        Create co_residency if any.
        """
        self.ensure_one()
        if self.co_residency_id:
            cor_id = self.co_residency_id
        else:
            vals = {"address_id": self.address_id.id}
            cor_id = self.env["co.residency"].create(vals)

        self_ctx = self.with_context(co_residency_id=cor_id.id)
        super(AllowDuplicateWizard, self_ctx).button_allow_duplicate()

        # go directly to the newly created co-residency
        res = cor_id.get_formview_action()
        if not self.co_residency_id:
            res["new_co_res"] = True
        return res
