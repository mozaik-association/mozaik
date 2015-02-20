# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_base, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_base is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_base is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_base.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp.tools import SUPERUSER_ID
from email.utils import formataddr


class mail_message(orm.Model):
    _inherit = "mail.message"

    def _get_default_from(self, cr, uid, context=None):
        """
        If force_from is into the context then use this email as email_from
        otherwise call super()
        """
        context = context or {}
        if context.get('force_from'):
            this = self.pool.get('res.users').browse(
                cr, SUPERUSER_ID, uid, context=context)
            return formataddr((this.name, this.email))
        return super(mail_message, self)._get_default_from(
            cr, uid, context=context)

    def _find_allowed_model_wise(self, cr, uid, doc_model, doc_dict, context=None):
        '''
        Do not test the active flag when retrieving the message_ids list
        '''
        context = context or {}
        ctx = context.copy()
        ctx.update({
            'active_test': False,
        })
        return super(mail_message, self)._find_allowed_model_wise(cr, uid, doc_model, doc_dict, context=ctx)
