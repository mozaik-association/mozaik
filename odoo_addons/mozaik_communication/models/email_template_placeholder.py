# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class EmailTemplatePlaceholder(models.Model):

    _inherit = 'email.template.placeholder'

    @api.model
    def _get_default_model_id(self):
        return self.env['ir.model'].search(
            [('model', '=', 'email.coordinate')])

    model_id = fields.Many2one(
        default=lambda s: s._get_default_model_id())
    placeholder = fields.Char(
        default='${object.partner_id.}')
