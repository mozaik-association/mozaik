# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class MailMailStatistics(models.Model):

    _inherit = 'mail.mail.statistics'
    res_id = fields.Integer(index=True)
    sent = fields.Datetime(index=True)
