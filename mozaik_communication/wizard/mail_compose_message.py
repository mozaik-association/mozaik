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
from openerp.tools import SUPERUSER_ID


class mail_compose_message(orm.TransientModel):

    _inherit = 'mail.compose.message'

    def get_mail_values(self, cr, uid, wizard, res_ids, context=None):
        """
        ===============
        get_mail_values
        ===============
        If the wizard's model is `email.coordinate` then the recipient is the
        email of the `email.coordinate`
        """
        values = super(mail_compose_message, self).get_mail_values(cr, uid, wizard, res_ids, context=context)
        email_path = context.get('email_coordinate_path', False)
        if email_path:
            for model_obj in self.pool[wizard.model].browse(cr, SUPERUSER_ID, values.keys(), context=context):
                email = eval('%s.%s' % ('model_obj', email_path))
                if email:
                    values[model_obj['id']].pop('recipient_ids', [])
                    values[model_obj['id']]['email_to'] = email
        return values

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
