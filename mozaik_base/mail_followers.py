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


class mail_notification(orm.Model):
    _inherit = 'mail.notification'

    def _notify_email(self, cr, uid, ids, message_id, force_send=False,
                      user_signature=True, context=None):
        force_send = context.get('notify_force_send', False)
        return super(mail_notification, self)._notify_email(
            cr, uid, ids, message_id, force_send=force_send,
            user_signature=user_signature, context=context)
