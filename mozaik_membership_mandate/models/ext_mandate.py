# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExtMandate(models.Model):

    _inherit = "ext.mandate"

    partner_instance_search_ids = fields.Many2many(
        relation="ext_mandate_partner_instance_membership_rel",
    )
