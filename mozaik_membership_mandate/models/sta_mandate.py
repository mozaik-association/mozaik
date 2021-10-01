# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StaMandate(models.Model):

    _inherit = "sta.mandate"

    partner_instance_search_ids = fields.Many2many(
        relation="sta_mandate_partner_instance_membership_rel",
    )
