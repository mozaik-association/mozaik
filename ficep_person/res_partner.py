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

import openerp
from openerp.osv import orm, fields

from openerp.addons.base.res import res_partner


# Constants
AVAILABLE_GENDERS = [
                     ('m', 'Male'),
                     ('f', 'Female'),
                    ]

available_genders = dict(AVAILABLE_GENDERS)

AVAILABLE_CIVIL_STATUS = [
                          ('u', 'Unmarried'), 
                          ('m', 'Married'), 
                          ('d', 'Divorced'),
                         ]

available_civil_status = dict(AVAILABLE_CIVIL_STATUS)

AVAILABLE_TONGUES = [
                     ('f', 'French'),
                     ('g', 'German'),
                    ]

available_tongues = dict(AVAILABLE_TONGUES)

class res_partner(orm.Model):

    _inherit = 'res.partner'

    _display_name_store_triggers = {
        'res.partner': (lambda self,cr,uid,ids,context=None: ids,
                        ['is_company', 'name', 'firstname', 'lastname', 'usual_firstname', 'usual_lastname',], 10)
    }

    _columns = {
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue', select=True, track_visibility='onchange'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender', select=True, track_visibility='onchange'),
        'civil_status': fields.selection(AVAILABLE_CIVIL_STATUS, 'Civil Status', track_visibility='onchange'),  
        'secondary_website': fields.char('Secondary Website', size=128, track_visibility='onchange',
                                         help="Secondary Website of Partner or Company"),
        'twitter': fields.char('Twitter', size=64, track_visibility='onchange'),
        'facebook': fields.char('Facebook', size=64, track_visibility='onchange'),
        'ldap_name': fields.char('LDAP Name', size=64, track_visibility='onchange',
                                 help="Name of the user in the LDAP"),
        'ldap_id': fields.integer('LDAP Id', track_visibility='onchange',
                                  help="ID of the user in the LDAP"),
        'usual_firstname': fields.char("Usual Firstname"),
        'usual_lastname': fields.char("Usual Lastname"),
            
        # Standard fields redefinition
        'display_name': fields.function(res_partner.res_partner._display_name_compute, type='char', string='Name', store=_display_name_store_triggers),
        'birthdate': fields.date('Birthdate', select=True, track_visibility='onchange'),
        'website': fields.char('Main Website', size=128, track_visibility='onchange',
                               help="Main Website of Partner or Company"),
        'comment': fields.text('Notes', select=True),

        # Validity period
        'create_date': fields.datetime('Creation Date', readonly=True),
        'expire_date': fields.datetime('Expiration Date', readonly=True, track_visibility='onchange'),
    }

    _defaults = {
        # Redefinition
        'tz': 'Europe/Brussels',
        'customer': False,
        'notification_email_send': 'none',
        
        # New fields 
        'tongue': lambda *args: AVAILABLE_TONGUES[0][0],
    }

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if 'show_address' in context:
            res = super(res_partner, self).name_get(cr, uid, ids, context=context)
        else:
            if isinstance(ids, (int, long)):
                ids = [ids]
            res = []
            for record in self.browse(cr, uid, ids, context=context):
                if record.is_company:
                    name = record.name
                else:
                    names = (
                             record.usual_lastname or record.lastname,
                             record.usual_firstname or record.firstname or False
                            )
                    name = " ".join([s for s in names if s])
                if context.get('show_email') and record.email:
                    name = "%s <%s>" % (name, record.email)
                res.append((record.id, name))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
