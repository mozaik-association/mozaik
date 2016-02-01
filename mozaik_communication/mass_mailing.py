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
from openerp.tools.translate import _


class MailMailStats(orm.Model):

    _inherit = 'mail.mail.statistics'

    def set_bounced(self, cr, uid, ids=None, mail_mail_ids=None,
                    mail_message_ids=None, context=None):
        """
        Increase the bounce counter of the email_coordinate
        """
        res_ids = super(MailMailStats, self).set_bounced(
            cr, uid, ids=ids, mail_mail_ids=mail_mail_ids,
            mail_message_ids=mail_message_ids, context=context)
        for stat in self.browse(cr, uid, res_ids, context=context):
            if stat.model == 'email.coordinate' and stat.res_id:
                active_ids = [stat.res_id]
            else:
                stat_model = self.pool[stat.model]
                email_key = stat_model.get_relation_column_name(
                    cr, uid, 'email.coordinate', context=context)
                if email_key:
                    vals = stat_model.read(
                        cr, uid, stat.res_id, [email_key], context=context)
                    active_ids = [vals[email_key][0]]

            if active_ids:
                ctx = context.copy()
                ctx['active_ids'] = active_ids
                wiz_id = self.pool['bounce.editor'].create(
                    cr, uid, {'increase': 1,
                              'model': 'email.coordinate',
                              'description': _('Invalid Email Address'),
                              }, context=context)
                self.pool['bounce.editor'].update_bounce_datas(
                    cr, uid, [wiz_id], context=ctx)

                # post technical details of the bounce on the sender document
                keep_bounce = self.pool['ir.config_parameter'].get_param(
                    cr, uid, 'mail.bounce.keep', default='1', context=context)
                bounce_body = context.get('bounce_body')
                if bounce_body and keep_bounce.lower() in ['1', 'true']:
                    email_coordinate = self.pool['email.coordinate']
                    email_coordinate.message_post(
                        cr, uid, active_ids[0],
                        subject='Bounce Details', body=bounce_body,
                        context=context)

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
        if mailing.distribution_list_id:
            if mailing.mailing_model == 'email.coordinate':
                ctx = dict(context or {},
                           main_object_field='email_coordinate_id',
                           main_target_model='email.coordinate')
                dl_obj = self.pool['distribution.list']
                res = dl_obj.get_complex_distribution_list_ids(
                    cr, uid, [mailing.distribution_list_id.id],
                    context=ctx)[0]
                return res
        return super(MassMailing, self).get_recipients(
            cr, uid, mailing, context=context)
