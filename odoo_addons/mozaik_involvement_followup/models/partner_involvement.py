# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from openerp import api, fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


STATE_TYPE = [
    ('nofollowup', 'Without follow-up'),
    ('followup', 'To follow'),
    ('late', 'Late follow-up'),
    ('done', 'Followed'),
]


class PartnerInvolvement(models.Model):

    _inherit = 'partner.involvement'

    _track = {
        'state': {
            'mozaik_involvement_followup.partner_involvement_to_follow_mms':
                lambda self, cr, uid, brec, c=None: brec.state == 'followup',
            'mozaik_involvement_followup.partner_involvement_late_mms':
                lambda self, cr, uid, brec, c=None: brec.state == 'late',
        },
    }

    state = fields.Selection(
        selection=STATE_TYPE, index=True,
        track_visibility='onchange', copy=False,
        default='nofollowup')

    deadline = fields.Date(
        index=True, copy=False, store=True,
        compute='_compute_deadline')

    @api.multi
    @api.depends("involvement_category_id")
    def _compute_deadline(self):
        for involvement in self:
            if involvement.involvement_category_id.nb_deadline_days:
                deadline = (date.today() + timedelta(
                    days=involvement.involvement_category_id.nb_deadline_days)
                ).strftime(DATE_FORMAT)
                involvement.deadline = deadline
            else:
                involvement.deadline = False

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        '''
        Launch followup if any
        '''
        res = super(PartnerInvolvement, self).create(vals)
        if res.deadline and not res.env.context.get('disable_followup'):
            cat = res.involvement_category_id.sudo()
            fol_ids = []
            if cat.mandate_category_id:
                fol_ids += cat.mandate_category_id._get_active_representative(
                    res.partner_instance_id.id, True)
            fol_ids += cat.message_follower_ids.ids
            res.message_subscribe(fol_ids)
            res.state = 'followup'
        return res

    @api.model
    def _set_state_as_late(self):
        '''
        Called by cron
        Change state of all 'followup' involvements with a passed deadline
        Effect is a tracking notification to subscribed followers to the
        corresponding subtype
        '''
        today = fields.date.today()
        invs = self.search([
            ('deadline', '!=', False),
            ('deadline', '<=', today),
            ('state', '=', 'followup'),
        ])
        invs.write({'state': 'late'})
        return True

    @api.multi
    def action_followup_done(self):
        self.write({'state': 'done'})
