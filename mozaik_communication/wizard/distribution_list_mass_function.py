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

import base64
from datetime import datetime

from openerp.tools.translate import _
from openerp.osv import orm, fields

# Constants
SORT_BY = [
    ('identifier', 'Identification Number'),
    ('display_name', 'Name'),
    ('country_id, zip, display_name', 'Zip Code'),
]
E_MASS_FUNCTION = [
    ('email_coordinate_id', 'Mass Mailing'),
    ('csv', 'CSV Extraction'),
    ('vcard', 'VCARD Extraction'),
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
    _description = 'Mass Function'

    _columns = {
        'trg_model': fields.selection(
            TRG_MODEL, string='Sending Mode', required=True),
        'e_mass_function': fields.selection(
            E_MASS_FUNCTION, string='Mass Function'),
        'p_mass_function': fields.selection(
            P_MASS_FUNCTION, string='Mass Function'),

        'distribution_list_id': fields.many2one(
            'distribution.list', string='Distribution List',
            required=True, ondelete='cascade'),

        'email_template_id': fields.many2one(
            'email.template', string='Email Template', ondelete='cascade'),
        'mass_mailing_name': fields.char(string='Mass Mailing Name'),
        'extract_csv': fields.boolean(
            string='Complementary Postal CSV',
            help="Get a CSV file for partners without email"),

        'postal_mail_name': fields.char(string='Postal Mailing Name'),
        'sort_by': fields.selection(SORT_BY, string='Sort by'),

        'bounce_counter': fields.integer(string='Maximum of Fails'),
        'include_unauthorized': fields.boolean(string='Include Unauthorized'),
        'internal_instance_id': fields.many2one(
            'int.instance', string='Internal Instance', ondelete='cascade'),

        'include_without_coordinate': fields.boolean(
            string='Include without Coordinate'),
        'groupby_coresidency': fields.boolean(string='Group by Co-Residency'),

        'export_file': fields.binary(string='File', readonly=True),
        'export_filename': fields.char(string='Export Filename', size=128),
    }

    _defaults = {
        'trg_model': 'email.coordinate',
        'distribution_list_id': lambda self, cr, uid, context:
            context.get('active_id', False),
        'include_unauthorized': False,
        'extract_csv': False,
        'include_without_coordinate': False,
        'groupby_coresidency': False,
    }

    def onchange_mass_function(self, cr, uid, ids, context=None):
        """
        Reset some fields when `mass_fucntion` change
        """
        return {
            'value': {
                'extract_csv': False,
                'export_filename': False,
                'include_without_coordinate': False,
            }
        }

    def onchange_trg_model(self, cr, uid, ids, context=None):
        """
        Reset some fields when `trg_model` change
        """
        return {
            'value': {
                'p_mass_function': False,
                'e_mass_function': False,
            }
        }

# public methods

    def mass_function(self, cr, uid, ids, context=None):
        """
        This method allow to make mass function on
        - email.coordinate
        - postal.coordinate
        """
        context = dict(context or {})
        file_exported = False
        composer = self.pool['mail.compose.message']
        mail_message = self.pool['mail.message']
        for wizard in self.browse(cr, uid, ids, context=context):
            domains = []
            if wizard.internal_instance_id:
                domains.append(
                    ('int_instance_id', 'child_of',
                     [wizard.internal_instance_id.id]))
            context['more_filter'] = domains
            context['target_model'] = wizard.trg_model
            fct = wizard.trg_model == 'email.coordinate' \
                and wizard.e_mass_function or wizard.p_mass_function
            if (fct == 'csv' or wizard.extract_csv) and \
                    wizard.include_without_coordinate:
                context['active_test'] = False
                context['field_alternative_object'] = 'id'

            if wizard.sort_by:
                context['sort_by'] = wizard.sort_by

            csv_model = wizard.trg_model

            if wizard.trg_model == 'email.coordinate':
                if not wizard.include_unauthorized:
                    domains.append(('email_unauthorized', '=', False))

                if wizard.bounce_counter:
                    wizard.bounce_counter = wizard.bounce_counter if \
                        wizard.bounce_counter >= 0 else 0
                    domains.append(
                        ('email_bounce_counter', '<=', wizard.bounce_counter))

                context['field_main_object'] = 'email_coordinate_id'

                if fct == 'csv':
                    #
                    # Get CSV containing email coordinates
                    #
                    active_ids, alternative_ids = self.pool[
                        'distribution.list'].get_complex_distribution_list_ids(
                            cr, uid, [wizard.distribution_list_id.id],
                            context=context)

                elif fct == 'email_coordinate_id':
                    #
                    # Send mass mailing
                    #
                    template_id = wizard.email_template_id.id
                    email_from = mail_message._get_default_from(
                        cr, uid, context=context)
                    dl_id = wizard.distribution_list_id and \
                        wizard.distribution_list_id.id or False
                    mail_composer_vals = {
                        'email_from': email_from,
                        'parent_id': False,
                        'use_active_domain': False,
                        'composition_mode': 'mass_mail',
                        'same_thread': True,
                        'post': False,
                        'partner_ids': [[6, False, []]],
                        'notify': False,
                        'template_id': template_id,
                        'subject': "",
                        'distribution_list_id': dl_id,
                        'mass_mailing_name': wizard.mass_mailing_name,
                        'model': wizard.trg_model}
                    value = composer.onchange_template_id(
                        cr, uid, ids, template_id, 'mass_mail', '', 0,
                        context=context)['value']
                    if value.get('attachment_ids'):
                        value['attachment_ids'] = [
                            [6, False, value['attachment_ids']]
                        ]
                    mail_composer_vals.update(value)
                    mail_composer_id = composer.create(
                        cr, uid, mail_composer_vals, context=context)

                    if wizard.extract_csv:
                        if not wizard.include_without_coordinate:
                            context['field_alternative_object'] = \
                                'postal_coordinate_id'
                        context['alternative_more_filter'] = [
                            ('email_coordinate_id', '=', False)]
                    active_ids, alternative_ids = self.pool[
                        'distribution.list'].get_complex_distribution_list_ids(
                            cr, uid, [wizard.distribution_list_id.id],
                            context=context)

                    if alternative_ids and wizard.extract_csv:
                        if wizard.postal_mail_name and \
                                not wizard.include_without_coordinate:
                            self._generate_postal_log(
                                cr, uid, wizard.postal_mail_name,
                                alternative_ids, context=context)
                    elif not active_ids:
                        raise orm.except_orm(
                            _('Error'), _('There are no recipients'))
                    context['active_ids'] = active_ids
                    context['dl_computed'] = True
                    context['email_coordinate_path'] = 'email'
                    composer.send_mail(
                        cr, uid, [mail_composer_id], context=context)
                    if alternative_ids and wizard.extract_csv:
                        fct = 'csv'
                        csv_model = 'postal.coordinate'
                        active_ids = alternative_ids

                elif fct == 'vcard':
                    #
                    # Get VCARD containing email coordinates
                    #
                    active_ids, __ = self.pool[
                        'distribution.list'].get_complex_distribution_list_ids(
                            cr, uid, [wizard.distribution_list_id.id],
                            context=context)
                    file_exported = self.export_vcard(cr, uid, ids,
                                                      active_ids, context)

            elif wizard.trg_model == 'postal.coordinate':
                if not wizard.include_unauthorized:
                    domains.append(('postal_unauthorized', '=', False))

                if wizard.bounce_counter:
                    wizard.bounce_counter = wizard.bounce_counter if \
                        wizard.bounce_counter >= 0 else 0
                    domains.append(
                        ('postal_bounce_counter', '<=', wizard.bounce_counter))

                context['field_main_object'] = 'postal_coordinate_id'

                if fct == 'csv':
                    #
                    # Get CSV containing postal coordinates
                    #
                    active_ids, alternative_ids = self.pool[
                        'distribution.list'].get_complex_distribution_list_ids(
                            cr, uid, [wizard.distribution_list_id.id],
                            context=context)

                    if wizard.postal_mail_name and \
                            not wizard.include_without_coordinate:
                        self.post_processing(
                            cr, uid, wizard, active_ids, context=context)
                        self._generate_postal_log(
                            cr, uid, wizard.postal_mail_name, active_ids,
                            context=context)

                elif fct == 'postal_coordinate_id':
                    #
                    # Get postal coordinate PDF labels
                    #
                    active_ids, alternative_ids = self.pool[
                        'distribution.list'].get_complex_distribution_list_ids(
                            cr, uid, [wizard.distribution_list_id.id],
                            context=context)
                    if wizard.postal_mail_name and \
                            not wizard.include_without_coordinate:
                        self.post_processing(
                            cr, uid, wizard, active_ids, context=context)
                    ctx = context.copy()
                    if wizard.groupby_coresidency:
                        to_print_ids = []
                        co_res_ids = []
                        for postal in self.pool['postal.coordinate'].browse(
                                cr, uid, active_ids, context=context):
                            if postal.co_residency_id:
                                if postal.co_residency_id.id not in\
                                        co_res_ids:
                                    co_res_ids.append(
                                        postal.co_residency_id.id)
                                    to_print_ids.append(postal.id)
                            else:
                                to_print_ids.append(postal.id)
                        active_ids = to_print_ids
                    ctx.update({
                        'active_model': 'postal.coordinate',
                        'active_ids': active_ids,
                        'groupby_co_residency': wizard.groupby_coresidency,
                    })
                    report = self.pool['report'].get_pdf(
                        cr, uid, active_ids,
                        report_name='mozaik_address.' +
                        'report_postal_coordinate_label', context=ctx)

                    pdf = base64.encodestring(report)

                    self.write(cr, uid, ids[0],
                               {'export_file': pdf,
                                'export_filename': 'report.pdf'},
                               context=context)
                    file_exported = True

                    if wizard.postal_mail_name:
                        self._generate_postal_log(
                            cr, uid, wizard.postal_mail_name, active_ids,
                            context=context)

            if fct == 'csv':
                if wizard.include_without_coordinate:
                    file_exported = self.export_csv(
                        cr, uid, ids, 'virtual.target', alternative_ids,
                        context=context)
                else:
                    file_exported = self.export_csv(
                        cr, uid, ids, csv_model, active_ids,
                        wizard.groupby_coresidency, context=context)

        if file_exported:
            return {
                'name': _('Mass Function'),
                'type': 'ir.actions.act_window',
                'res_model': 'distribution.list.mass.function',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': ids[0],
                'views': [(False, 'form')],
                'target': 'new',
            }

    def _generate_postal_log(self, cr, uid,
                             postal_mail_name, postal_coordinate_ids,
                             context=None):
        """
        Generate a postal mailing for the specified parameters:
        * postal mailing name
        * postal coordinate ids
        """
        if not postal_coordinate_ids:
            return True
        now = datetime.now()
        postal_mail_log_obj = self.pool['postal.mail.log']
        postal_mail_id = self.pool['postal.mail'].create(cr, uid, {
            'name': postal_mail_name,
            'sent_date': now,
        }, context=context)

        coords = self.pool['postal.coordinate'].browse(
            cr, uid, postal_coordinate_ids, context=context)
        for coord in coords:
            postal_mail_log_obj.create(cr, uid, {
                'postal_mail_id': postal_mail_id,
                'postal_coordinate_id': coord.id,
                'partner_id': coord.partner_id.id,
                'sent_date': now,
            }, context=context)

        return True

    def export_csv(self, cr, uid, ids, model, model_ids, group_by=False,
                   context=None):
        """
        Export the specified coordinates to a CSV file.
        """
        csv_content = self.pool.get('export.csv').get_csv(
            cr, uid, model, model_ids, group_by=group_by, context=context)

        csv_content = base64.encodestring(csv_content)

        self.write(cr, uid, ids[0],
                   {'export_file': csv_content,
                    'export_filename': 'extract.csv'},
                   context=context)

        return True

    def export_vcard(self, cr, uid, ids, email_coordinate_ids, context=None):
        """
        ============
        export_vcard
        ============
        Export the specified coordinates to a VCF file.
        :type email_coordinate_ids: []
        """
        vcard_content = self.pool.get('export.vcard').get_vcard(
            cr, uid, email_coordinate_ids, context=context)
        vcard_content = base64.encodestring(vcard_content)

        self.write(cr, uid, ids[0],
                   {'export_file': vcard_content,
                    'export_filename': 'extract.vcf'},
                   context=context)

        return True

    def post_processing(self, cr, uid, wizard, active_ids, context=None):
        pass
