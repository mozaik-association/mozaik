# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class MailMail(models.Model):

    _inherit = 'mail.mail'

    @api.model
    def create(self, vals):
        # set priority if any
        if 'priority' not in vals and self.env.context.get('job_priority'):
            vals['priority'] = self.env.context['job_priority']
        return super(MailMail, self).create(vals)
