# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Nemry Jonathan
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm


class MailMail(orm.Model):

    _inherit = 'mail.mail'

    def _get_unsubscribe_url(
            self, cr, uid, mail, email_to, msg=None, context=None):
        '''
        Override native method to manage unsubscribe URL for distribution list
        case of newsletter.
        '''
        mml = mail.mailing_id
        if mml.distribution_list_id and mml.distribution_list_id.newsletter:
            return super(MailMail, self)._get_unsubscribe_url(
                cr, uid, mail, email_to, msg=msg, context=context)
        else:
            return False
