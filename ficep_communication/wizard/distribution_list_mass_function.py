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
import csv
import tempfile
from collections import OrderedDict

from openerp.tools.translate import _
from openerp.osv import orm, fields

from openerp.addons.ficep_person.res_partner import available_genders, available_tongues

HEADER_ROW = [
    'Lastname',
    'Usual Lastname',
    'Firstname',
    'Usual Firstname',
    'Co-Residency Line 1',
    'Co-Residency Line 2',
    'Country Code',
    'Country Name',
    'Country Zip',
    'Street',
    'Street2',
    'City',
    'Birthdate',
    'Gender',
    'Tongue',
    'Phone',
    'Mobile',
    'Fax',
    'Email'
]

# Constants
SORT_BY = [
    ('identification_number asc', 'Identification Number'),
    ('display_name asc', 'Name'),
    ('zip desc,display_name asc', 'Zip Code'),
]
E_MASS_FUNCTION = [
    ('email_coordinate_id', 'Mass Mailing'),
    ('csv', 'CSV Extraction'),
]
P_MASS_FUNCTION = [
    ('postal_coordinate_id', 'Label Printing'),
    ('csv', 'CSV Extraction'),
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
        'campaign_id': fields.many2one('mail.mass_mailing.campaign', 'Mail Campaign', select=True),
        'extract_csv': fields.boolean('CSV Extraction',
                                      help="Get a CSV file with all partners who have no email coordinate"),

        'sort_by': fields.selection(SORT_BY, 'Sort by'),

        'bounce_counter': fields.integer('Maximum of Fails'),
        'include_unauthorized': fields.boolean('Include Unauthorized'),
        'internal_instance_id': fields.many2one('int.instance', 'Internal Instance'),

        'groupby_coresidency': fields.boolean('Group by Co-Residency'),
    }

    _defaults = {
         'trg_model': 'email.coordinate',
     }

    def onchange_trg_model(self, cr, uid, ids, context=None):
        return {
            'value': {
                'p_mass_function': '',
                'e_mass_function': '',
             }
        }

# public methods

    def mass_function(self, cr, uid, ids, context=None):
        """
        =============
        mass function
        =============
        """
        composer = self.pool['mail.compose.message']
        for wizard in self.browse(cr, uid, ids, context=context):
            if wizard.trg_model == 'email.coordinate':
                domains = []
                if wizard.include_unauthorized:
                    domains.append("'|',('email_unauthorized','=', True),('email_unauthorized','=', False)")
                else:
                    domains.append("('email_unauthorized','=', False)")

                if wizard.internal_instance_id:
                    domains.append("('int_instance_id','child_of', [%s])" % wizard.internal_instance_id.id)
                if wizard.bounce_counter != 0:
                    wizard.bounce_counter = wizard.bounce_counter if wizard.bounce_counter >= 0 else 0
                    domains.append("('email_bounce_counter','<=', %s)" % wizard.bounce_counter)
                context['more_filter'] = domains

                if wizard.sort_by:
                    context['sort_by'] = wizard.sort_by
                if wizard.groupby_coresidency:
                    context['alternative_group_by'] = 'co_residency_id'

                if wizard.e_mass_function == 'csv':
                    pass
                else:
                    context['field_alternative_object'] = 'postal_coordinate_id'
                    context['field_main_object'] = wizard.e_mass_function
                    context['target_model'] = wizard.trg_model
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
                                          'template_id': template_id,
                                          'subject': "",
                                          'mass_mailing_campaign_id': wizard.campaign_id.id,
                                          'model': wizard.trg_model}
                    value = composer.onchange_template_id(cr, uid, ids, template_id, 'mass_mail', '', 0, context=context)['value']
                    mail_composer_vals.update(value)
                    mail_composer_id = composer.create(cr, uid, mail_composer_vals, context=context)
                    # compute ids
                    active_ids, alternative_ids = self.pool['distribution.list'].get_complex_distribution_list_ids(cr, uid, [context.get('active_id', False)], context=context)
                    context['active_ids'] = active_ids
                    if alternative_ids and wizard.extract_csv:
                        self.render_csv(cr, uid, alternative_ids, wizard.groupby_coresidency, context=context)

                    self.pool['mail.compose.message'].send_mail(cr, uid, [mail_composer_id], context=context)
            else:
                # TODO: label print
                pass

    def render_csv(self, cr, uid, postal_ids, group_by=False, context=None):
        """
        ==========
        render_csv
        ==========
        Get a CSV file with data of postal_ids depending of ``HEADER_ROW``
        Send  the CSV as message into the inbox of the user
        :type postal_ids: []
        """
        def safe_get(o, attr, default=None):
            try:
                return getattr(o, attr)
            except orm.except_orm:
                return default

        postal_coordinates = self.pool['postal.coordinate'].browse(cr, uid, postal_ids, context=context)
        tmp = tempfile.NamedTemporaryFile(prefix='Extract', suffix=".csv", delete=False)
        f = open(tmp.name, "r+")
        writer = csv.writer(f)
        writer.writerow(HEADER_ROW)
        co_residencies = []
        for pc in postal_coordinates:
            #case group by is ask and where a co_residency is present and already write then don't write a new row
            if group_by and pc.co_residency_id and pc.co_residency_id.id in co_residencies:
                continue
            co_residencies.append(pc.co_residency_id.id)
            #test access coordinate (VIP READER)
            partner = safe_get(pc, 'partner_id')
            if not partner:
                continue

            writer.writerow([
                 partner.lastname or None,
                 partner.usual_lastname or None,
                 partner.firstname or None,
                 partner.usual_firstname or None,

                 partner.printable_name if not pc.co_residency_id \
                    else pc.co_residency_id.line,
                 pc.co_residency_id if not pc.co_residency_id \
                    else pc.co_residency_id.line2,
                 pc.address_id.country_code or None,
                 pc.address_id.country_id.name or None,
                 pc.address_id.zip or None,
                 pc.address_id.street or None,
                 pc.address_id.street2 or None,
                 pc.address_id.city or None,
                 partner.birth_date or None,
                 available_genders.get(partner.gender, None),
                 available_tongues.get(partner.tongue, None),
                 partner.fix_coordinate_id if not partner.fix_coordinate_id \
                    else partner.fix_coordinate_id.phone_id.name,
                 partner.mobile_coordinate_id if not partner.mobile_coordinate_id \
                    else partner.mobile_coordinate_id.phone_id.name,
                 partner.fax_coordinate_id if not partner.fax_coordinate_id \
                    else partner.fax_coordinate_id.phone_id.name,
                 partner.email_coordinate_id if not partner.email_coordinate_id \
                    else partner.email_coordinate_id.email
             ])
        f.close()
        f = open(tmp.name, "r")
        attachment = [(_('Extract.csv'), '%s' % f.read())]
        partner_ids = self.pool['res.partner'].search(cr, uid, [('user_ids', '=', uid)], context=context)
        if partner_ids:
            self.pool['mail.thread'].message_post(cr, uid, False, attachments=attachment, context=context, partner_ids=partner_ids, subject=_('Export CSV'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
