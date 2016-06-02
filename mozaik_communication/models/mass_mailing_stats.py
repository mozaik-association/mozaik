# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class MailMailStats(models.Model):

    _inherit = 'mail.mail.statistics'

    @api.multi
    @api.depends('res_id', 'model')
    def _compute_email_coordinate_id(self):
        '''
        Transform res_id integers to real email coordinates ids
        '''
        coord_ids = [
            stat.res_id for stat in self
            if stat.model == 'email.coordinate' and stat.res_id
        ]
        coords = self.env['email.coordinate'].search(
            [('id', 'in', coord_ids)])
        for stat in self:
            if stat.res_id in coords.ids:
                stat.email_coordinate_id = stat.res_id
            else:
                stat.email_coordinate_id = False

    email_coordinate_id = fields.Many2one(
        comodel_name='email.coordinate', string='Email Coordinate',
        compute='_compute_email_coordinate_id', store=True,
        ondelete='cascade')
