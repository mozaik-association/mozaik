# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    distribution_list_opt_out_ids = fields.Many2many(
        comodel_name='distribution.list',
        relation='distribution_list_res_partner_out',
        column1='partner_id',
        column2='distribution_list_id',
        string='Opt-Out',
        domain=[('newsletter', '=', True)],
        oldname="opt_out_ids",
    )
    distribution_list_opt_in_ids = fields.Many2many(
        comodel_name='distribution.list',
        relation='distribution_list_res_partner_in',
        column1='partner_id',
        column2='distribution_list_id',
        string='Opt-In',
        domain=[('newsletter', '=', True)],
        oldname="opt_in_ids",
    )
    responsible_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible User',
        index=True,
    )
