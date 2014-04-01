# -*- coding: utf-8 -*-
##############################################################################
#
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
from openerp.tools import mail


class mail_mail(orm.Model):

    _inherit = 'mail.mail'

# public methods

    def generate_email(self, cr, uid, subject, body, recipients, context=None):
        """
        ==============
        generate_email
        ==============
        :type body: char
        :param body: string to be converted into a HTML content
        :type subject: char
        :param subject: subject of the mail
        :type recipients: [integer]
        :param recipients: list of partner ids

        **Note**
        Create a mail.mail with a body content ``body`` and recipients ``recipients``
        """
        recipient_ids = [[6, False, recipients]]
        html_body = mail.plaintext2html(body)
        self.create(cr, uid, {'subject': subject,
                              'recipient_ids': recipient_ids,
                              'body_html': html_body,
                              }, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
