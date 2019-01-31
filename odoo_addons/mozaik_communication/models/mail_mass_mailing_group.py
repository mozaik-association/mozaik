# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class MassMailingGroup(models.Model):

    _name = 'mail.mass_mailing.group'
    _description = 'Mass Mailing Group'

    name = fields.Char(
        compute='_compute_name', store=True)
    mailings_ids = fields.One2many(
        'mail.mass_mailing', 'group_id', string='Mailings')
    distribution_list_id = fields.Many2one(
        'distribution.list', string='Distribution List')
    total_sent = fields.Integer(
        compute='_compute_total_sent', store=True,
        string="Total sent (%)")

    # save fields from wizard
    include_unauthorized = fields.Boolean(string='Include Unauthorized')
    bounce_counter = fields.Integer(string='Maximum of Fails')
    internal_instance_id = fields.Many2one(
        'int.instance', string='Internal Instance')
    partner_from_id = fields.Many2one('res.partner', string='From')
    partner_name = fields.Char()

    @api.multi
    @api.depends(
        'mailings_ids.group_id',
        'mailings_ids.contact_ab_pc'
    )
    def _compute_total_sent(self):
        for group in self:
            group.total_sent = sum(group.mailings_ids.mapped('contact_ab_pc'))

    @api.multi
    @api.depends(
        'distribution_list_id',
    )
    def _compute_name(self):
        for group in self:
            group.name = '%s (#%s)' % (
                group.distribution_list_id.name, group.id)
