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

# Constants
SORT_BY = [
    ('register_number', 'Register Number'),
    ('name', 'Name'),
    ('zip', 'Zip'),
]
E_MASS_FUNCTION = [
    ('email_coordinate_id', 'Mass Mailing'),
    ('csv', 'CSV'),
]
P_MASS_FUNCTION = [
    ('postal_coordinate_id', 'Label Printing'),
    ('csv', 'CSV'),
]
TRG_MODEL = [
    ('email.coordinate', 'Email Coordinate'),
    ('postal.coordinate', 'Postal Coordinate'),
]


class distribution_list_mass_function(orm.TransientModel):

    _name = 'distribution.list.mass.function'
    _description = 'Distribution List Mass Function'

    _columns = {
        'trg_model': fields.selection(TRG_MODEL, 'Target Model', required=True),
        'e_mass_function': fields.selection(E_MASS_FUNCTION, 'Mass Function'),
        'p_mass_function': fields.selection(P_MASS_FUNCTION, 'Mass Function'),

        'email_template_id': fields.many2one('email.template', 'Email Template', select=True),
        'campaign_id': fields.many2one('mail.mass_mailing.campaign', 'Campaign', select=True),
        'extract_csv': fields.boolean('Extract CSV',
                                      help="Get a CSV file with all partners who have no email coordinate"),

        'sort_by': fields.selection(SORT_BY, 'Sort By'),

        'max_fails': fields.integer('Maximum of Fails'),
        'include_unauthorized': fields.boolean('Include Unauthorized'),
        'internal_instance_id': fields.many2one('int.instance', 'Internal Instance'),

        'groupby_coresidency': fields.boolean('Group By Co-Residency'),
    }

    _defaults = {
         'max_fails': 0,
         'trg_model': 'email.coordinate',
     }

    def onchange_trg_model(self, cr, uid, ids, context=None):
        return {
            'value': {
                'p_mass_function': '',
                'e_mass_function': '',
             }
        }

#public methods

    def mass_function(self, cr, uid, ids, context=None):
        """
        =============
        mass function
        =============
        """
        composer = self.pool['mail.compose.message']
        for wizard in self.browse(cr, uid, ids, context=context):
            if wizard.trg_model == 'email.coordinate':
                if wizard.e_mass_function == 'csv':
                    pass
                else:
                    context['field_mailing_object'] = wizard.e_mass_function
                    template_id = wizard.email_template_id.id
                    email_from = composer._get_default_from(cr, uid, context=context)
                    mail_composer_vals = {'email_from': email_from,
                                          'parent_id': False,
                                          'use_active_domain': False,
                                          'composition_mode': 'mass_mail',
                                          'same_thread': True,
                                          'post': False,
                                          'partner_ids': [[6, False, []]],
                                          'notify': False,
                                          'distribution_list_id': context.get('active_id', False),
                                          'template_id': template_id,
                                          'subject': "",
                                          'mass_mailing_campaign_id': wizard.campaign_id.id,
                                          'model': wizard.trg_model}
                    value = composer.onchange_template_id(cr, uid, ids, template_id, 'mass_mail', '', 0, context=context)['value']
                    mail_composer_vals.update(value)
                    mail_composer_id = composer.create(cr, uid, mail_composer_vals, context=context)
                    self.pool['mail.compose.message'].send_mail(cr, uid, [mail_composer_id], context=context)
            else:
                #TODO: label print
                pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
