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


class mail_compose_message(orm.TransientModel):

    _inherit = 'mail.compose.message'

    def get_mail_values(self, cr, uid, wizard, res_ids, context=None):
        """
        ===============
        get_mail_values
        ===============
        """
        values = super(mail_compose_message, self).get_mail_values(cr, uid, wizard, res_ids, context=context)
        if wizard.model == 'email.coordinate':
            #due to security terms
            email_values = self.pool[wizard.model].search_read(cr, uid, [('id', 'in', values.keys())], ['id', 'email'], context=context)
            for email_value in email_values:
                if email_value['email']:
                    values[email_value['id']]['email_to'] = email_value['email']
        return values

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
