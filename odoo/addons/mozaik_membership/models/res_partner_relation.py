# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class PartnerRelation(models.Model):

    _inherit = ['res.partner.relation']

    left_instance_id = fields.Many2one(
        related='left_partner_id.int_instance_id',
        string='Subject Internal Instance',
        index=True, readonly=True, store=True)
    right_instance_id = fields.Many2one(
        related='right_partner_id.int_instance_id',
        string='Object Internal Instance',
        index=True, readonly=True, store=True)
