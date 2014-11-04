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

from datetime import datetime, date

from openerp.tools.translate import _
from openerp.osv import orm, fields

# Constants
SORT_BY = [
    ('identifier asc', 'Identification Number'),
    ('display_name asc', 'Name'),
    ('country_id, zip asc,display_name asc', 'Zip Code'),
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
        'trg_model': fields.selection(TRG_MODEL, 'Sending Mode', required=True),
        'e_mass_function': fields.selection(E_MASS_FUNCTION, 'Mass Function'),
        'p_mass_function': fields.selection(P_MASS_FUNCTION, 'Mass Function'),

        'distribution_list_id': fields.many2one(
            'distribution.list', string='Distribution List',
            required=True, ondelete='cascade'),

        'email_template_id': fields.many2one(
            'email.template', string='Email Template', ondelete='cascade'),
        'mass_mailing_name': fields.char('Mass Mailing'),
        'extract_csv': fields.boolean('Complementary Postal CSV',
                                      help="Get a CSV file for partners without email"),

        'postal_mail_name': fields.char('Postal Mailing Name'),

        'sort_by': fields.selection(SORT_BY, 'Sort by'),

        'set_memcard_date': fields.boolean('Set Member Card Sent Date'),
        'set_del_doc_date': fields.boolean('Set Welcome Documents Sent Date'),

        'bounce_counter': fields.integer('Maximum of Fails'),
        'include_unauthorized': fields.boolean('Include Unauthorized'),
        'internal_instance_id': fields.many2one(
            'int.instance', string='Internal Instance', ondelete='cascade'),

        'groupby_coresidency': fields.boolean('Group by Co-Residency'),
    }

    _defaults = {
        'trg_model': 'email.coordinate',
        'distribution_list_id': lambda self, cr, uid, context:
            context.get('active_id', False),
    }

    def onchange_trg_model(self, cr, uid, ids, context=None):
        """
        ==================
        onchange_trg_model
        ==================
        reset `p_mass_function` and `e_mass_function`
        when `trg_model` is changed
        """
        return {
            'value': {
                'p_mass_function': False,
                'e_mass_function': False,
                'extract_csv': False,
                'set_memcard_date': False,
            }
        }

# public methods

    def mass_function(self, cr, uid, ids, context=None):
        """
        =============
        mass function
        =============
        This method allow to make mass function on
        - email.coordinate
        - postal.coordinate
        """
        composer = self.pool['mail.compose.message']
        for wizard in self.browse(cr, uid, ids, context=context):
            if wizard.trg_model == 'email.coordinate':
                domains = []

                if wizard.include_unauthorized:
                    domains.append('|')
                    domains.append(('email_unauthorized', '=', True))
                    domains.append(('email_unauthorized', '=', False))
                else:
                    domains.append(('email_unauthorized', '=', False))

                if wizard.internal_instance_id:
                    domains.append(
                        ('int_instance_id', 'child_of',
                         ['%s' % wizard.internal_instance_id.id]))

                if wizard.bounce_counter != 0:
                    wizard.bounce_counter = wizard.bounce_counter if wizard.bounce_counter >= 0 else 0
                    domains.append(
                        ('email_bounce_counter', '<=',
                         '%s' % wizard.bounce_counter))

                context['more_filter'] = domains
                context['target_model'] = wizard.trg_model
                if wizard.sort_by:
                    context['sort_by'] = wizard.sort_by
                if wizard.groupby_coresidency:
                    context['alternative_group_by'] = 'co_residency_id'

                if wizard.e_mass_function == 'csv':
                    #
                    # Get CSV containing email coordinates
                    #

                    context['field_main_object'] = 'email_coordinate_id'
                    active_ids, alternative_ids = self.pool['distribution.list'].get_complex_distribution_list_ids(cr, uid, [wizard.distribution_list_id.id], context=context)
                    self.export_csv(cr, uid, wizard.trg_model, active_ids, wizard.groupby_coresidency, context=context)

                elif wizard.e_mass_function == 'email_coordinate_id':
                    #
                    # Send mass mailing
                    #
                    context['field_alternative_object'] = 'postal_coordinate_id'
                    context['field_main_object'] = wizard.e_mass_function
                    template_id = wizard.email_template_id.id
                    email_from = composer._get_default_from(cr, uid, context=context)
                    dl_id = wizard.distribution_list_id and \
                        wizard.distribution_list_id.id or False
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
                                          'distribution_list_id': dl_id,
                                          'mass_mailing_name': wizard.mass_mailing_name,
                                          'model': wizard.trg_model}
                    value = composer.onchange_template_id(cr, uid, ids, template_id, 'mass_mail', '', 0, context=context)['value']
                    mail_composer_vals.update(value)
                    mail_composer_id = composer.create(cr, uid, mail_composer_vals, context=context)
                    context['alternative_more_filter'] = [('email_coordinate_id', '=', False)]

                    active_ids, alternative_ids = self.pool['distribution.list'].get_complex_distribution_list_ids(cr, uid, [wizard.distribution_list_id.id], context=context)
                    context['active_ids'] = active_ids
                    context['dl_computed'] = True
                    context['email_coordinate_path'] = 'email'
                    if alternative_ids and wizard.extract_csv:
                        self.export_csv(cr, uid, 'postal.coordinate', alternative_ids, wizard.groupby_coresidency, context=context)
                        if wizard.postal_mail_name:
                            self._generate_postal_log(cr, uid, wizard.postal_mail_name, alternative_ids, context=context)
                    if not active_ids:
                        raise orm.except_orm(
                            _('Error'), _('There are no recipients'))
                    composer.send_mail(cr, uid, [mail_composer_id], context=context)

                elif wizard.e_mass_function == 'vcard':
                    context['field_main_object'] = 'email_coordinate_id'
                    context['target_model'] = wizard.trg_model
                    active_ids, alternative_ids = self.pool['distribution.list'].get_complex_distribution_list_ids(cr, uid, [wizard.distribution_list_id.id], context=context)
                    self.export_vcard(cr, uid, active_ids, context)

            elif wizard.trg_model == 'postal.coordinate':
                domains = []

                if wizard.include_unauthorized:
                    domains.append('|')
                    domains.append(('postal_unauthorized', '=', True))
                    domains.append(('postal_unauthorized', '=', False))
                else:
                    domains.append(('postal_unauthorized', '=', False))

                if wizard.internal_instance_id:
                    domains.append(('int_instance_id', 'child_of',
                                    ['%s' % wizard.internal_instance_id.id]))
                if wizard.sort_by:
                    context['sort_by'] = wizard.sort_by
                if wizard.groupby_coresidency:
                    context['alternative_group_by'] = 'co_residency_id'

                context['more_filter'] = domains

                if wizard.p_mass_function == 'csv':
                    #
                    # Get CSV containing postal coordinates
                    #
                    context['field_main_object'] = 'postal_coordinate_id'
                    context['target_model'] = wizard.trg_model
                    active_ids, alternative_ids = self.pool['distribution.list'].get_complex_distribution_list_ids(cr, uid, [wizard.distribution_list_id.id], context=context)
                    self.select_date(
                        cr, uid, wizard.set_memcard_date,
                        wizard.set_del_doc_date, active_ids, context=context)
                    self.export_csv(cr, uid, wizard.trg_model, active_ids, wizard.groupby_coresidency, context=context)

                    if wizard.postal_mail_name:
                        self._generate_postal_log(cr, uid, wizard.postal_mail_name, active_ids, context=context)

                if wizard.p_mass_function == 'postal_coordinate_id':
                    #
                    # Get postal coordinate labels PDF
                    #
                    context['more_filter'] = domains
                    context['field_main_object'] = 'postal_coordinate_id'
                    context['target_model'] = wizard.trg_model
                    active_ids, alternative_ids = self.pool['distribution.list'].get_complex_distribution_list_ids(cr, uid, [wizard.distribution_list_id.id], context=context)
                    self.select_date(
                        cr, uid, wizard.set_memcard_date,
                        wizard.set_del_doc_date, active_ids, context=context)
                    ctx = context.copy()
                    ctx.update({
                        'active_model': 'postal.coordinate',
                        'active_ids': active_ids,
                    })
                    report = self.pool['report'].get_pdf(cr, uid, active_ids, report_name='mozaik_address.report_postal_coordinate_label', context=ctx)

                    if wizard.postal_mail_name:
                        self._generate_postal_log(cr, uid, wizard.postal_mail_name, active_ids, context=context)

                    attachment = [('report.pdf', report)]
                    partner_ids = self.pool['res.partner'].search(cr, uid, [('user_ids', '=', uid)], context=context)
                    if partner_ids:
                        self.pool['mail.thread'].message_post(cr, uid, False, attachments=attachment, context=context, partner_ids=partner_ids, subject=_('Export PDF'))

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

    def export_csv(self, cr, uid, model, model_ids, group_by=False, context=None):
        """
        ==========
        export_csv
        ==========
        Export the specified coordinates to a CSV file.
        """
        csv_content = self.pool.get('export.csv').get_csv(cr, uid, model, model_ids, group_by=group_by, context=context)
        attachment = [('extract.csv', csv_content)]
        partner_ids = self.pool['res.partner'].search(cr, uid, [('user_ids', '=', uid)], context=context)
        if partner_ids:
            self.pool['mail.thread'].message_post(cr, uid, False, attachments=attachment, context=context,
                                                  partner_ids=partner_ids, subject=_('Export CSV'))

        return True

    def export_vcard(self, cr, uid, email_coordinate_ids, context=None):
        """
        ============
        export_vcard
        ============
        Export the specified coordinates to a VCF file.
        :type email_coordinate_ids: []
        """
        vcard_content = self.pool.get('export.vcard').get_vcard(cr, uid, email_coordinate_ids, context=context)
        attachment = [('extract.vcf', vcard_content)]
        partner_ids = self.pool['res.partner'].search(cr, uid, [('user_ids', '=', uid)], context=context)
        if partner_ids:
            self.pool['mail.thread'].message_post(cr, uid, False, attachments=attachment, context=context,
                                                  partner_ids=partner_ids, subject=_('Export VCF'))

        return True

    def select_date(
            self, cr, uid, set_memcard_date,
            set_del_doc_date, active_ids, context=None):
        # impact delivery member card date of associated partner
        dates_to_update = []
        if set_memcard_date and active_ids:
            dates_to_update.append('del_mem_card_date')
        if set_del_doc_date and active_ids:
            dates_to_update.append('del_doc_date')
        if dates_to_update:
            self.set_date(
                cr, uid, active_ids, dates_to_update, context=context)

    def set_date(self, cr, uid, postal_coordinate_ids,
                 dates_to_update, context=None):
        '''
        This method will set the date `dates_to_update` for each partner of
        `postal.coordinate` concerned by `postal_coordinate_ids`
        :type postal_coordinate_ids: [integer]
        :param postal_coordinate_ids: ids of `postal.coordinate`
        :type date_to_update: [char]
        :param date_to_update: name of the field to update
        '''
        postal_coordinate_obj = self.pool['postal.coordinate']
        partner_obj = self.pool['res.partner']
        partner_ids = []
        candidate_ids = []
        for postal_coordinate in postal_coordinate_obj.browse(
                cr, uid, postal_coordinate_ids, context=context):
            partner = postal_coordinate.partner_id
            partner_ids.append(partner.id)
            if partner.membership_state_id.code == 'member_candidate':
                candidate_ids.append(partner.id)
        date_today = fields.date.today()
        vals = {}
        for date_to_update in dates_to_update:
            vals[date_to_update] = '%s' % date_today
        if partner_ids:
            partner_obj.write(cr, uid, partner_ids, vals, context=context)
        if candidate_ids:
            partner_obj.update_membership_reference(
                cr, uid, candidate_ids, context=context)
