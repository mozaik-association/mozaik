# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):

    _inherit = "res.partner"

    int_instance_id = fields.Many2one(
        comodel_name="int.instance",
        compute="_compute_int_instance_id",
        inverse="_inverse_instance_ids",
        compute_sudo=True,
        store=True,
    )

    @api.depends("int_instance_ids")
    def _compute_int_instance_id(self):
        for p in self:
            p.int_instance_id = p.int_instance_ids

    @api.constrains("int_instance_ids")
    def _check_int_instance_id(self):
        for p in self:
            # in some cases force_int_instance_id is removed after the create,
            # so we need to allow it
            if len(p.int_instance_ids - p.force_int_instance_id) > 1:
                raise ValidationError(
                    _("A partner (%s) cannot have more than one instance") % p.id
                )
