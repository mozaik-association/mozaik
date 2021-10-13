# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerRelation(models.AbstractModel):

    _inherit = "res.partner.relation"

    left_partner_instance_ids = fields.Many2many(
        comodel_name="int.instance",
        string="left Partner Internal Instances",
        related="left_partner_id.int_instance_ids",
        readonly=True,
    )

    right_partner_instance_ids = fields.Many2many(
        comodel_name="int.instance",
        string="Right Partner Internal Instances",
        related="right_partner_id.int_instance_ids",
        readonly=True,
    )
