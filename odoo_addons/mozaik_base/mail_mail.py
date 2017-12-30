# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class MailMail(models.Model):

    _inherit = 'mail.mail'

    @api.model
    def _get_partner_access_link(self, mail, partner=None):
        """
        By default disable trailing shortcut in mails
        """
        res = None
        if not self.env.context.get('disable_trailing_shortcut', True):
            res = super(MailMail, self)._get_partner_access_link(
                mail, partner=partner)
        return res

    @api.multi
    def send(self, auto_commit=False, raise_exception=False):
        '''
        workarounds:
        * execute always send with a context
        * switch auto_commit and context if params wrongly passed by JS
        '''
        ctx = self.env.context
        if not ctx:
            if isinstance(auto_commit, dict):
                ctx = auto_commit
                auto_commit = False
        if not ctx:
            ctx = self.env.user._context_get()
        if not self.env.context:
            self = self.with_context(ctx)
        res = super(MailMail, self).send(
            auto_commit=auto_commit, raise_exception=raise_exception)
        return res
