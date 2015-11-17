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
from openerp.tools import SUPERUSER_ID


class mail_compose_message(orm.TransientModel):

    _inherit = 'mail.compose.message'

    def get_mail_values(self, cr, uid, wizard, res_ids, context=None):
        """
        If the wizard's model is `email.coordinate` then the recipient is the
        email of the `email.coordinate`
        """
        values = super(mail_compose_message, self).get_mail_values(
            cr, uid, wizard, res_ids, context=context)
        email_path = context.get('email_coordinate_path', False)
        if email_path:
            for model_obj in self.pool[wizard.model].browse(
                    cr, SUPERUSER_ID, values.keys(), context=context):
                email = eval('%s.%s' % ('model_obj', email_path))
                if email:
                    values[model_obj['id']].pop('recipient_ids', [])
                    values[model_obj['id']]['email_to'] = email
        return values

    def _transient_vacuum(self, cr, uid, force=False):
        """
        Do not unlink mail composer wizards if unfinished jobs exist
        """
        res = True
        domain = [('state', '!=', 'done')]
        job_ids = self.pool['queue.job'].search(cr, uid, domain)
        if not job_ids:
            res = super(mail_compose_message, self)._transient_vacuum(
                cr, uid, force=force)
        return res

    def send_mail(self, cr, uid, ids, context=None):
        """
        Do not recompute ids if sending mails asynchronously
        """
        context = context or {}
        if context.get('not_async'):
            context = dict(context, dl_computed=True)
        else:
            pass
        return super(mail_compose_message, self).send_mail(
            cr, uid, ids, context=context)
