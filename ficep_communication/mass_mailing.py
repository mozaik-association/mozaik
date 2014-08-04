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
from openerp.osv import orm, fields
from openerp.tools.translate import _


class MailMailStats(orm.Model):

    _inherit = 'mail.mail.statistics'

    def set_bounced(self, cr, uid, ids=None, mail_mail_ids=None, mail_message_ids=None, context=None):
        """
        ===========
        set_bounced
        ===========
        This overload is made to spread the bounce counter to the email_coordinate.
        Only work for message that have `email.coordinate` as model
        """
        res_ids = super(MailMailStats, self).set_bounced(cr, uid, ids=ids, mail_mail_ids=mail_mail_ids, mail_message_ids=mail_message_ids, context=context)
        for stat in self.browse(cr, uid, res_ids, context=context):
            if stat.model == 'email.coordinate' and stat.res_id:
                active_ids = [stat.res_id]
            else:
                email_key = self.pool.get(stat.model).get_relation_column_name(cr, uid, 'email.coordinate', context=context)
                if email_key:
                    active_ids = [self.pool.get(stat.model).read(cr, uid, stat.res_id, [email_key], context=context)[email_key]]

            if active_ids:
                ctx = context.copy()
                ctx['active_ids'] = [stat.res_id]
                wiz_id = self.pool['bounce.editor'].create(cr, uid, {'increase': 1,
                                                                     'model': 'email.coordinate',
                                                                     'description': _('Invalid Email Address'),
                                                                      }, context=context)
                self.pool['bounce.editor'].update_bounce_datas(cr, uid, [wiz_id], context=ctx)
        return res_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
