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
from openerp.tools import SUPERUSER_ID
from openerp.tools.translate import _
from openerp.tools import mail

CONCERNED_BY_DUPLICATE = ['postal.coordinate',
                          'email.coordinate',
                          'phone.coordinate',
                          'res.partner'
                          ]


class res_partner(orm.Model):

    _inherit = 'res.partner'

# data model

    _columns = {
        # relation fields
        'partner_is_subject_relation_ids': fields.one2many('partner.relation', 'subject_partner_id', string='Is Subject Of Relation', domain=[('active', '=', True)]),
        'partner_is_object_relation_ids': fields.one2many('partner.relation', 'object_partner_id', string='Is Object Of Relation', domain=[('active', '=', True)]),

        'partner_is_subject_relation_inactive_ids': fields.one2many('partner.relation', 'subject_partner_id', string='Is Subject Of Relation', domain=[('active', '=', False)]),
        'partner_is_object_relation_inactive_ids': fields.one2many('partner.relation', 'object_partner_id', string='Is Object Of Relation', domain=[('active', '=', False)]),
    }

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy o2m fields.
        Reset some fields to their initial values.
        """
        default = default or {}
        default.update({
            'partner_is_subject_relation_ids': [],
            'partner_is_object_relation_ids': [],
            'partner_is_subject_relation_inactive_ids': [],
            'partner_is_object_relation_inactive_ids': [],
        })
        res = super(res_partner, self).copy_data(cr, uid, ids, default=default, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """
        =====
        write
        =====
        When invalidating a partner, invalidates also its partner.relation
        """
        res = super(res_partner, self).write(cr, uid, ids, vals, context=context)
        if 'active' in vals and not vals['active']:
            relation_obj = self.pool['partner.relation']
            relations_ids = []
            for partner in self.browse(cr, SUPERUSER_ID, ids, context=context):
                relations_ids += [c.id for c in partner.partner_is_subject_relation_ids]
                relations_ids += [c.id for c in partner.partner_is_object_relation_ids]
            if relations_ids:
                relation_obj.button_invalidate(cr, SUPERUSER_ID, relations_ids, context=context)
        return res

#pûblic methods

    def process_notify_duplicate(self, cr, uid, ids=None, force_send=False, context=None):
        """
        ========================
        process_notify_duplicate
        ========================
        1) Get All Partner IDs having a configurator user
        1") If No Configurator then abort
        2) Search All Duplicate
        3) Construct a Body with Needed Data
        4) Create a mail.mail with those informations
        5) Send Email
        """
        model, group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ficep_base', 'ficep_res_groups_configurator')
        configurator_group = self.pool.get(model).browse(cr, uid, [group_id], context=context)[0]
        if configurator_group.users:
            partner_ids = [(p.partner_id.id)for p in configurator_group.users]
            if partner_ids:
                subject = _('OpenERP-Duplicate Notification')
                content_text = []
                for model_concerned in CONCERNED_BY_DUPLICATE:
                    value = self.pool.get(model_concerned).get_string_duplicates(cr, SUPERUSER_ID, context=context)
                    if value:
                        content_text.append(value)
                if content_text:
                    text_body = '\n\n'.join(content_text)
                else:
                    text_body = _('There Are No Duplicate Detected')
                recipient_ids = [[6, False, partner_ids]]
                html_body = mail.plaintext2html(text_body)
                return self.pool.get('mail.mail').create(cr, uid, {'subject': subject,
                                                                   'recipient_ids': recipient_ids,
                                                                   'body_html': html_body,
                                                                   }, context=context)
        return -1

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
