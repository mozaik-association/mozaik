# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class MailMail(models.Model):

    _inherit = 'mail.mail'

    @api.model
    def _get_partner_access_link(self, mail, partner=None):
        """
        Do not disable trailing shortcut for involvements
        """
        if mail.model == 'partner.involvement' and mail.res_id \
                and mail.notification and partner and partner.user_ids:
            self = self.with_context(disable_trailing_shortcut=False)
        res = super(MailMail, self)._get_partner_access_link(
            mail, partner=partner)
        return res

    @api.model
    def send_get_mail_subject(
            self, mail, force=False, partner=None):
        """ build another subject for an involvement notification """
        res = None
        if mail.model == 'partner.involvement' and mail.res_id \
                and mail.notification:
            involvement = self.env['partner.involvement'].search(
                [('id', '=', mail.res_id)])
            if involvement:
                res = '%s: %s' % (
                    mail.record_name, involvement.partner_id.display_name)
        if not res:
            res = super(MailMail, self).send_get_mail_subject(
                mail, force=force, partner=partner)
        return res
