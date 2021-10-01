# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AbstractMandate(models.AbstractModel):

    _inherit = 'abstract.mandate'

    partner_instance_ids = fields.Many2many(
        related='partner_id.int_instance_ids',
        string='Partner Internal Instances',
        readonly=True,
    )
    partner_instance_search_ids = fields.Many2many(
        comodel_name="int.instance",
        related="partner_id.int_instance_ids",
        store=True,
        column1="mandate_id",
        column2="instance_id",
    )
