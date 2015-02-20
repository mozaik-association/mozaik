# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_communication, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_communication is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_communication is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_communication.
#     If not, see <http://www.gnu.org/licenses/>.
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
            return ''
