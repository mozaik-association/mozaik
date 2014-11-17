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

import datetime

from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID
from openerp.tools.translate import _


class postal_mail(orm.Model):
    _name = "postal.mail"
    _inherit = ['mozaik.abstract.model']
    _description = 'Postal Mailing'

    _inactive_cascade = True

    def _postal_mail_log_count(self, cr, uid, ids, field_name, arg, context=None):
        PostalMailLog = self.pool('postal.mail.log')
        return {
            postal_mail_id: PostalMailLog.search_count(cr, uid, [('postal_mail_id', '=', postal_mail_id)],
                                                       context=context)
            for postal_mail_id in ids
        }

    _columns = {
        'name': fields.char('Name', size=256, required=True, track_visibility='onchange'),
        'sent_date': fields.date('Sent Date', required=True, track_visibility='onchange'),
        'postal_mail_log_count': fields.function(_postal_mail_log_count, string="Log Count", type="integer"),
    }

    _defaults = {
        'sent_date': fields.date.today,
    }

    _order = 'sent_date desc, name'

# constraints

    _unicity_keys = 'name'

# orm methods

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy o2m fields.
        Reset some fields to their initial values.
        """
        default = default or {}
        default.update({
            'sent_date': datetime.date.today(),
        })
        res = super(postal_mail, self).copy_data(cr, uid, ids, default=default, context=context)
        res.update({
            'name': _('%s (copy)') % res.get('name'),
        })
        return res

    def name_get(self, cr, uid, ids, context=None):
        """
        ========
        name_get
        ========
        :rparam: list of (id, name)
                 where id is the id of each object
                 and name, the name to display.
        :rtype: [(id, name)] list of tuple
        """
        if not ids:
            return []
        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []
        for record in self.browse(cr, uid, ids, context=context):
            res.append((record['id'], '%s (%s)' %
                        (record.name, record.sent_date,)))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, uid, ['|', ('name', operator, name),
                                        ('sent_date', operator, name)] + args,
                              limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)


class postal_mail_log(orm.Model):
    _name = "postal.mail.log"
    _inherit = ['mozaik.abstract.model']
    _description = 'Postal Mail Log'

    _int_instance_store_trigger = {
        'postal.mail.log': (
            lambda self, cr, uid, ids, context=None: ids, ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['postal.mail.log'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _columns = {
        'name': fields.char('Name', size=256, track_visibility='onchange'),
        'sent_date': fields.date('Sent Date', required=True, track_visibility='onchange'),
        'postal_mail_id': fields.many2one('postal.mail', 'Postal Mailing', readonly=True),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate', required=True),
        'partner_id': fields.many2one('res.partner', string='Partner', required=True),
        'partner_instance_id': fields.related(
            'partner_id', 'int_instance_id',
            string='Partner Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_int_instance_store_trigger),
    }

    _defaults = {
        'sent_date': fields.date.today,
    }

    _order = 'sent_date desc, partner_id'

# constraints

    _unicity_keys = 'N/A'

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        """
        ========
        name_get
        ========
        :rparam: list of (id, name)
                 where id is the id of each object
                 and name, the name to display.
        :rtype: [(id, name)] list of tuple
        """
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []
        for record in self.browse(cr, uid, ids, context=context):
            res.append((record['id'], record.name or record.postal_mail_id.name))

        return res

    def copy(self, cr, uid, ids, default=None, context=None):
        """
        ====
        copy
        ====
        Do not copy if postal_mail_id is set.
        """
        flds = self.read(cr, uid, ids, ['postal_mail_id'], context=context)
        if flds.get('postal_mail_id', False):
            raise orm.except_orm(_('Error'), _('A postal mail log cannot be copied when linked to a postal mailing!'))
        res = super(postal_mail_log, self).copy(cr, uid, ids, default=default, context=context)
        return res

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Set date to today and append (copy) to the name.
        """
        default = default or {}
        default.update({
            'sent_date': datetime.date.today(),
        })
        res = super(postal_mail_log, self).copy_data(
            cr, uid, ids, default=default, context=context)
        res.update({
            'name': _('%s (copy)') % res.get('name'),
        })
        return res

# view methods: onchange, button

    def onchange_postal_coordinate_id(
            self, cr, uid, ids, postal_coordinate_id, partner_id,
            context=None):
        """
        Set the partner_id to the id of the partner
        of the selected postal coordinate.
        """
        if postal_coordinate_id:
            partner_id = self.pool['postal.coordinate'].read(
                cr, uid, [postal_coordinate_id], ['partner_id'],
                context=context)[0]['partner_id'][0]

        return {
            'value': {
                'partner_id': partner_id,
            }
        }

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        """
        Set the domain of the postal coordinate to restrict the selection
        to coordinates having the specified partner_id.
        """
        domain = partner_id and [('partner_id', '=', partner_id)] or []

        return {
            'domain': {
                'postal_coordinate_id': domain,
            }
        }
