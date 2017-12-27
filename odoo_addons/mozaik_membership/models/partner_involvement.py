# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models

import openerp.addons.decimal_precision as dp


class PartnerInvolvement(models.Model):

    _inherit = 'partner.involvement'

    partner_instance_id = fields.Many2one(
        comodel_name='int.instance', string='Partner Internal Instance',
        related='partner_id.int_instance_id', store=True, readonly=True)

    amount = fields.Float(
        digits=dp.get_precision('Product Price'),
        copy=False, track_visibility='onchange')
    reference = fields.Char(copy=False, track_visibility='onchange')

    _sql_constraints = [
        (
            'donation',
            "CHECK (involvement_type IS NULL OR "
            "involvement_type != 'donation' OR amount > 0.0)",
            'For a donation amount must be positive !',
        ),
    ]
