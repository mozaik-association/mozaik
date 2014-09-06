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


class MassMailingList(orm.Model):

    _name = "mail.mass_mailing.list"
    _inherit = ['mail.mass_mailing.list', 'abstract.ficep.model']

    _columns = {
        'int_instance_id': fields.many2one(
            'int.instance', 'Internal Instance',
            select=True, track_visibility='onchange'),
        'automatic': fields.boolean('Automatic'),
        # visible from portal
        'public': fields.boolean('Public'),
    }

    _unicity_keys = 'name, int_instance_id'


class MassMailingContact(orm.Model):

    _name = "mail.mass_mailing.contact"
    _inherit = ['mail.mass_mailing.contact', 'abstract.ficep.model']
    _rec_name = "partner_id"

    def _get_email(self, cr, uid, ids, name, args, context=None):
        """
        :param ids: `mail.mass_mailing.contact` ids for which `email` has to
            be recomputed
        :rparam: dictionary for all mailing contact id with email
        :rtype: dict {integer: char, ...}
        :exception: `partner_id` of the `mail.mass_mailing.contact` has no
            email coordinate
        :Note:
        Calling and result convention: Single mode
        """
        context = context or {}
        result = {i: False for i in ids}

        for mailing in self.browse(cr, uid, ids, context=context):
            partner = mailing.partner_id
            email = partner.email_coordinate_id and \
                partner.email_coordinate_id.email or False
            if not email:
                raise orm.except_orm(_('Error'), _('Partner must have an email ' +
                                             'coordinate'))
            result[mailing.id] = email
        return result

    _email_store_triggers = {
        'mail.mass_mailing.contact': (lambda s, cr, uid, ids, c: ids,
                                      ['partner_id'], 10),
        'email.coordinate': (lambda self, cr, uid, ids, context=None:
                             self.pool['email.coordinate']._get_linked_mailing(
                                 cr, uid, ids, context=context),
                             ['active', 'is_main'], 10),
    }

    _columns = {
        'partner_id': fields.many2one(
            'res.partner', 'Partner', required=True, select=True),
        'email': fields.function(
            _get_email, type='char', string='email',
            track_visibility='onchange', store=_email_store_triggers),
    }

    _unicity_keys = 'list_id, partner_id'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
