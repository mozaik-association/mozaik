# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class PartnerInvolvement(models.Model):

    _inherit = 'partner.involvement'

    partner_instance_id = fields.Many2one(
        comodel_name='int.instance', string='Partner Internal Instance',
        related='partner_id.int_instance_id', store=True, readonly=True)

    amount = fields.Float(
        digits=dp.get_precision('Product Price'),
        copy=False, track_visibility='onchange')
    reference = fields.Char(copy=False, track_visibility='onchange')
    promise = fields.Boolean(
        string='Just a promise',
        compute='_compute_promise', store=True)

    _sql_constraints = [
        (
            'donation',
            "CHECK (active IS FALSE OR involvement_type IS NULL OR "
            "involvement_type NOT IN ('donation') OR amount > 0.0)",
            'For a donation amount must be positive !',
        ),
    ]

    @api.multi
    @api.depends("effective_time", "reference", "involvement_type")
    def _compute_promise(self):
        for involvement in self:
            involvement.promise = (
                involvement.involvement_type in ['donation'] and
                involvement.reference and
                not involvement.effective_time
            )
