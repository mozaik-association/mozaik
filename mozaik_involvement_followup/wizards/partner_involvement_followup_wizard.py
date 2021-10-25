# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class PartnerInvolvementFollowupWizard(models.TransientModel):

    _name = 'partner.involvement.followup.wizard'

    @api.model
    def _next_category_ids_domain(self):
        '''
        Compute domain for next_category_ids
        '''
        domain = []
        inv_ids = self.env.context.get(
            'active_ids') or [self.env.context.get('active_id')] or []
        if inv_ids:
            current_fols = self.env['partner.involvement'].browse(
                inv_ids).mapped('involvement_category_id')
            next_fols = current_fols and \
                current_fols[0].involvement_category_ids or \
                self.env['partner.involvement.category']
            for fol in current_fols:
                next_fols &= fol.involvement_category_ids
            if next_fols:
                domain = [('id', 'in', next_fols.ids)]
        return domain

    @api.model
    def _get_followup(self):
        types = [
            ('delay', _('I added some other followers, follow-up continue, '
                        'the deadline is postponed (by number of '
                        'days defined on the category)')),
            ('done', _('Follow-up is done, I added details in '
                       'the note or in the history')),
            ('continue', _('This follow-up is done, '
                           'but it continues by starting next follow-up')),
        ]
        dom = self._next_category_ids_domain()
        if dom:
            return types
        return types[:-1]

    @api.model
    def _default_followup(self):
        choices = self._get_followup()
        return choices[-1][0]

    followup = fields.Selection(
        selection='_get_followup',
        default=lambda s: s._default_followup())

    next_category_ids = fields.Many2many(
        'partner.involvement.category',
        relation='followup_wizard_partner_involvement_category_rel',
        column1='followup_wizard_id', column2='partner_category_id',
        string='Next Follow-up Categories',
        domain=lambda s: s._next_category_ids_domain())

    def doit(self):
        self.ensure_one()
        inv_ids = self.env.context.get(
            'active_ids') or [self.env.context.get('active_id')] or []

        action = {'type': 'ir.actions.act_window_close'}

        if not inv_ids:
            return action

        invs = self.env['partner.involvement'].browse(inv_ids)
        today = fields.Date.today()
        now = fields.Datetime.now()
        for inv in invs:
            if self.followup == 'delay':
                # just update the deadline and log a message
                deadline = inv.deadline
                inv.write({'from_date': today})
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
                        inv.create(vals)
        return action
