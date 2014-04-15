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


class distribution_list_mailing(orm.TransientModel):

    _name = 'distribution.list.mailing'
    _description = 'Distribution List Mailing'

    _columns = {
        'email_template_id': fields.many2one('email.template', 'Email Template', required=True, select=True),
        'campaign_id': fields.many2one('mail.mass_mailing.campaign', 'Campaign', required=True, select=True),
    }

    def mass_mailing(self, cr, uid, ids, context=None):
        """
        ============
        mass_mailing
        ============
        Create a `mail.compose.message` having a `email.template` and a
        `mass_mailing.campaign`
        """
        composer = self.pool['mail.compose.message']
        for wizard in self.browse(cr, uid, ids, context=context):
            template_id = wizard.email_template_id.id
            mail_composer_vals = {'composition_mode': 'mass_mail',
                                  'email_from': 'admin@example.com',
                                  'same_thread': True,
                                  'distribution_list_id': context.get('active_id', False),
                                  'template_id': template_id,
                                  'parent_id': False,
                                  'subject': "${object.email}",
                                  'mass_mailing_campaign_id': wizard.campaign_id.id,
                                  'model': 'email.coordinate'}
            value = composer.onchange_template_id(cr, uid, ids, template_id, 'mass_mail', '', 0, context=context)['value']
            mail_composer_vals.update(value)
            mail_composer_id = composer.create(cr, uid, mail_composer_vals, context=context)
            self.pool['mail.compose.message'].send_mail(cr, uid, [mail_composer_id], context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
