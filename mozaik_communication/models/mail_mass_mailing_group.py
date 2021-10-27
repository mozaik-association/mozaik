# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class MassMailingGroup(models.Model):
    _name = 'mail.mass_mailing.group'
    _description = 'Mass Mailing Group'

    name = fields.Char(
        compute='_compute_name',
        store=True,
    )
    mailings_ids = fields.One2many(
        comodel_name='mailing.mailing',
        inverse_name='group_id',
        string='Mailings',
    )
    distribution_list_id = fields.Many2one(
        comodel_name='distribution.list',
        string='Distribution List',
    )
    internal_instance_id = fields.Many2one(
        comodel_name='int.instance',
    )
    total_sent = fields.Integer(
        compute='_compute_total_sent',
        store=True,
        string="Total sent (%)",
    )

    @api.depends(
        'mailings_ids.group_id',
        'mailings_ids.contact_ab_pc'
    )
    def _compute_total_sent(self):
        for group in self:
            group.total_sent = sum(group.mailings_ids.mapped('contact_ab_pc'))

    @api.depends(
        'distribution_list_id',
    )
    def _compute_name(self):
        for group in self:
            group.name = '%s (#%s)' % (group.distribution_list_id.name,
                                       group.id)
