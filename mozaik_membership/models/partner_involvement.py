# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PartnerInvolvement(models.Model):

    _inherit = "partner.involvement"

    partner_instance_ids = fields.Many2many(
        comodel_name="int.instance",
        string="Partner Internal Instances",
        related="partner_id.int_instance_ids",
        readonly=True,
    )
