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


class postal_mail(orm.Model):
    _name = "postal.mail"
    _inherit = ['abstract.ficep.model']
    _description = 'Postal Mail'

    def _postal_mail_log_count(self, cr, uid, ids, field_name, arg, context=None):
        PostalMailLog = self.pool('postal.mail.log')
        return {
            postal_mail_id: PostalMailLog.search_count(cr, uid, [('postal_mail_id', '=', postal_mail_id)],
                                                       context=context)
            for postal_mail_id in ids
        }

    _columns = {
        'name': fields.char('Name', size=256, track_visibility='onchange'),
        'sent_date': fields.datetime('Sent date', track_visibility='onchange'),
        'postal_mail_log_ids': fields.one2many('postal.mail.log', 'postal_mail_id', 'Postal Mail Logs'),
        'postal_mail_log_count': fields.function(_postal_mail_log_count, string="Log Count", type="integer"),
    }

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
            'postal_mail_log_ids': [],
            'sent_date': False,
        })
        res = super(postal_mail, self).copy_data(cr, uid, ids, default=default, context=context)
        return res


class postal_mail_log(orm.Model):
    _name = "postal.mail.log"
    _inherit = ['abstract.ficep.model']
    _description = 'Postal Mail Log'

    _columns = {
        'name': fields.char('Name', size=256, track_visibility='onchange'),
        'sent_date': fields.datetime('Sent date', track_visibility='onchange'),
        'postal_mail_id': fields.many2one('postal.mail', 'Postal Mail', track_visibility='onchange'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate', track_visibility='onchange'),
        'partner_id': fields.related('postal_coordinate_id', 'partner_id', string='Partner', type='many2one',
                                     relation='res.partner', track_visibility='onchange'),
    }

# constraints

    _unicity_keys = 'N/A'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
