# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _

FOLLOWUP_TYPE = [
    ('delay', 'I added some other followers, follow-up continue, '
     'please just increase the deadline'),
    ('done', 'Follow-up is done, I added details in '
     'the note or in the history'),
    ('continue', 'Follow-up here is now done, it continues '
     'by starting next follow-up'),
]


class PartnerInvolvementFollowupWizard(models.TransientModel):

    _name = 'partner.involvement.followup.wizard'

    @api.model
    def _default_current_category_id(self):
        inv_id = self.env.context.get('active_id') or False
        if inv_id:
            return self.env['partner.involvement'].browse(
                inv_id).involvement_category_id
        return False

    followup = fields.Selection(
        selection=FOLLOWUP_TYPE, default='continue')

    current_category_id = fields.Many2one(
        'partner.involvement.category',
        string='Current Follow-up Category',
        default=lambda s: s._default_current_category_id())

    next_category_ids = fields.Many2many(
        'partner.involvement.category',
        relation='followup_wizard_partner_involvement_category_rel',
        column1='followup_wizard_id', column2='partner_category_id',
        string='Next Follow-up Categories')

    @api.onchange('current_category_id')
    def _onchange_current_category_id(self):
        '''
        Compute domain for next_category_ids m2m
        '''
        domain = [
            ('id', 'in', self.current_category_id.involvement_category_ids.ids)
        ]
        return {
            'domain': {
                'next_category_ids': domain
            }
        }

    @api.multi
    def doit(self):
        self.ensure_one()
        inv_id = self.env.context.get('active_id') or False

        action = {'type': 'ir.actions.act_window_close'}

        if not inv_id:
            return action
        inv = self.env['partner.involvement'].browse(inv_id)
        now = fields.Datetime.now()
        if self.followup == 'delay':
            # just update the deadline and log a message
            deadline = inv.deadline
            inv.write({'from_date': fields.Date.today()})
            if deadline != inv.deadline:
                inv.message_post(
                    body=_('Additionnal follow-up delay: %s => %s') % (
                        deadline, inv.deadline),
                    type='comment')
        else:
            # mark involvement as done
            inv.write({'state': 'done', 'effective_time': now})
            if self.followup == 'continue':
                for cat in self.next_category_ids:
                    vals = {
                        'partner_id': inv.partner_id.id,
                        'involvement_category_id': cat.id,
                    }
                    new_inv = inv.create(vals)
                action = {
                    'type': 'ir.actions.act_window',
                    'name': 'Follow-up: Next Involvement',
                    'res_model': 'partner.involvement',
                    'res_id': new_inv.id,
                    'view_mode': 'form,tree',
                }
        return action
