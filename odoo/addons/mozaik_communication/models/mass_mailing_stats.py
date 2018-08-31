# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class MailMailStats(models.Model):
    _inherit = 'mail.mail.statistics'

    email_coordinate_id = fields.Many2one(
        comodel_name='email.coordinate',
        string='Email Coordinate',
        compute='_compute_email_coordinate_id',
        store=True,
        ondelete='cascade',
    )

    @api.multi
    @api.depends('res_id', 'model')
    def _compute_email_coordinate_id(self):
        """
        Transform res_id integers to real email coordinates ids
        :return:
        """
        target_model = 'email.coordinate'
        coordinate_ids = self.filtered(
            lambda m: m.res_id and m.model == target_model).mapped("res_id")
        coordinates = self.env[target_model].browse(coordinate_ids).exists()
        for stat in self:
            if stat.model == target_model and stat.res_id in coordinates.ids:
                stat.email_coordinate_id = stat.res_id
            else:
                stat.email_coordinate_id = False
