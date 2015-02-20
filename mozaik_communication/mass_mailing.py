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

from openerp.osv import orm, fields
from openerp.tools.translate import _
import openerp.tools as tools
from openerp.tools import SUPERUSER_ID


class MailMailStats(orm.Model):

    _inherit = 'mail.mail.statistics'

    def set_bounced(self, cr, uid, ids=None, mail_mail_ids=None, mail_message_ids=None, context=None):
        """
        ===========
        set_bounced
        This overload is made to spread the bounce counter to the email_coordinate.
        ===========
        Only work for message that have `email.coordinate` as model
        """
        res_ids = super(MailMailStats, self).set_bounced(cr, uid, ids=ids, mail_mail_ids=mail_mail_ids, mail_message_ids=mail_message_ids, context=context)
        for stat in self.browse(cr, uid, res_ids, context=context):
            if stat.model == 'email.coordinate' and stat.res_id:
                active_ids = [stat.res_id]
            else:
                email_key = self.pool.get(stat.model).get_relation_column_name(cr, uid, 'email.coordinate', context=context)
                if email_key:
                    active_ids = [self.pool.get(stat.model).read(cr, uid, stat.res_id, [email_key], context=context)[email_key][0]]

            if active_ids:
                ctx = context.copy()
                ctx['active_ids'] = active_ids
                wiz_id = self.pool['bounce.editor'].create(cr, uid, {'increase': 1,
                                                                     'model': 'email.coordinate',
                                                                     'description': _('Invalid Email Address'),
                                                                      }, context=context)
                self.pool['bounce.editor'].update_bounce_datas(cr, uid, [wiz_id], context=ctx)
        return res_ids


class MassMailing(orm.Model):

    _inherit = 'mail.mass_mailing'

    _defaults = {
        'mailing_model': 'email.coordinate',
    }

    def _get_mailing_model(self, cr, uid, context=None):
        '''
        Remove last insert: `mail.mass_mailing.contact`
        '''
        res = super(MassMailing, self)._get_mailing_model(
            cr, uid, context=context)
        if res:
            # remove last insert: mailing list
            res.pop(len(res)-1)
        return res

    def get_recipients(self, cr, uid, mailing, context=None):
        """
        Override this method to get resulting ids of the distribution list
        """
        context = context or {}
        if mailing.distribution_list_id:
            context['field_main_object'] = 'email_coordinate_id'
            dl_obj = self.pool['distribution.list']
            if mailing.mailing_model == 'email.coordinate':
                res = dl_obj.get_complex_distribution_list_ids(
                    cr, uid, [mailing.distribution_list_id.id],
                    context=context)[0]
                return res
        return super(MassMailing, self).get_recipients(
            cr, uid, mailing, context=context)
