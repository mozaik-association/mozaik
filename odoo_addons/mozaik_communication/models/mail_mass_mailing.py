# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import random

from openerp import api, fields, models


class MassMailing(models.Model):

    _inherit = 'mail.mass_mailing'

    create_uid =  fields.Many2one('res.users', readonly=True)
    group_id = fields.Many2one(
        'mail.mass_mailing.group', copy=True)
    group_total_sent = fields.Integer(
        related='group_id.total_sent')
    mailing_model = fields.Char(default='email.coordinate')

    @api.model
    def _get_mailing_model(self):
        '''
        Remove last insert: `mail.mass_mailing.contact`
        '''
        res = super(MassMailing, self)._get_mailing_model()
        if res:
            # remove last insert: mailing list
            res.pop()
        return res

    @api.model
    def get_recipients(self, mailing):
        """
        Override this method to get resulting ids of the distribution list
        """
        if mailing.distribution_list_id:
            if mailing.mailing_model == 'email.coordinate':
                dl = mailing.distribution_list_id.with_context(
                    main_object_field='email_coordinate_id',
                    main_target_model='email.coordinate'
                )
                res = dl.get_complex_distribution_list_ids()[0]
                if mailing.contact_ab_pc < 100 and mailing.group_id:
                    topick = int(len(res) / 100.0 * mailing.contact_ab_pc)
                    already_mailed = self.env['mail.mail.statistics'].search([
                        ('mass_mailing_id.group_id', '=', mailing.group_id.id),
                    ]).mapped('res_id')
                    remaining = set(res).difference(already_mailed)
                    if topick > len(remaining):
                        topick = len(remaining)
                    res = random.sample(remaining, topick)
                return res
        return super(MassMailing, self).get_recipients(mailing)

    @api.multi
    def send_custom(self):
        self.ensure_one()
        group = self.group_id
        unsent_percent = (100 - group.total_sent)
        wiz = self.env['distribution.list.mass.function'].create({
            'trg_model': 'email.coordinate',
            'e_mass_function': 'email_coordinate_id',
            'mass_mailing_name': self.name,
            'subject': self.name,
            'body': self.body_html,
            'contact_ab_pc': unsent_percent,
            'distribution_list_id': group.distribution_list_id.id,
            'include_unauthorized': group.include_unauthorized,
            'internal_instance_id': group.internal_instance_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz.id,
            'res_model': wiz._name,
            'target': 'new',
            'context': dict(self.env.context, mailing_group_id=group.id),
        }

    @api.multi
    def compare_group(self):
        self.ensure_one()
        group = self.group_id
        context = dict(
            self.env.context,
            search_default_group_id=group.id,
            group_by='trial',
        )
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'graph',
            'res_model': 'mail.statistics.report',
            'context': context,
        }
