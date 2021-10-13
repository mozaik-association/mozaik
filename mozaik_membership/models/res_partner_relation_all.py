# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerRelationAll(models.AbstractModel):

    _inherit = "res.partner.relation.all"

    this_partner_instance_ids = fields.Many2many(
        comodel_name="int.instance",
        string="This Partner Internal Instances",
        related="this_partner_id.int_instance_ids",
        readonly=True,
    )

    other_partner_instance_ids = fields.Many2many(
        comodel_name="int.instance",
        string="Other Partner Internal Instances",
        related="other_partner_id.int_instance_ids",
        readonly=True,
    )
