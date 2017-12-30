# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class PartnerInvolvementCategory(models.Model):

    _inherit = 'partner.involvement.category'

    nb_deadline_days = fields.Integer(
        string='Number of days before deadline',
        default=0, track_visibility='onchange',
        help="0 = no follow-up on children involvements")

    mandate_category_id = fields.Many2one(
        'mandate.category', string='Mandate Category',
        domain=[('type', '=', 'int')],
        index=True, track_visibility='onchange')

    _sql_constraints = [
        (
            'nb_deadline_days_no_negative',
            'CHECK (nb_deadline_days >= 0)',
            'Number of days before deadline cannot be negative !',
        ),
        (
            'mandate_category_without_deadline',
            'CHECK (mandate_category_id IS NULL OR nb_deadline_days > 0)',
            'Without deadline rule mandate category must be null !',
        ),
    ]

    @api.onchange('nb_deadline_days')
    def _onchange_nb_deadline_days(self):
        if not self.nb_deadline_days:
            self.mandate_category_id = False
