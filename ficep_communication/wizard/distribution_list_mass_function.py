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
import vobject
import codecs
from datetime import datetime

from openerp.tools.translate import _
from openerp.osv import orm, fields

from openerp.addons.ficep_person.res_partner import available_genders, available_tongues

HEADER_ROW = [
    'Lastname',
    'Usual Lastname',
    'Firstname',
    'Usual Firstname',
    'Internal Identifier',
    'Co-Residency Line 1',
    'Co-Residency Line 2',
    'Main Address',
    'Unauthorized Address',
    'Vip Address',
    'Country Code',
    'Country Name',
    'Zip',
    'Street',
    'Street2',
    'City',
    'Internal Instance',
    'Birthdate',
    'Gender',
    'Tongue',
    'Main Phone',
    'Unauthorized Phone',
    'Vip Phone',
    'Phone',
    'Main Mobile',
    'Unauthorized Mobile',
    'Vip Mobile',
    'Mobile',
    'Main Fax',
    'Unauthorized Fax',
    'Vip Fax',
    'Fax',
    'Main Email',
    'Unauthorized Email',
    'Vip Email',
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
    _description = 'Distribution List Mass Function'

    _columns = {
        'trg_model': fields.selection(TRG_MODEL, 'Sending Mode', required=True),
        'e_mass_function': fields.selection(E_MASS_FUNCTION, 'Mass Function'),
        'p_mass_function': fields.selection(P_MASS_FUNCTION, 'Mass Function'),

        'email_template_id': fields.many2one('email.template', 'Email Template'),
        'campaign_id': fields.many2one('mail.mass_mailing.campaign', 'Mail Campaign'),
        'extract_csv': fields.boolean('Complementary Postal CSV',
                                      help="Get a CSV file with all partners who have no email coordinate"),

        'postal_mail_id': fields.many2one('postal.mail', 'Postal mail'),

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
                    domains.append("'|',('email_unauthorized','=', True),('email_unauthorized','=', False)")
                else:
                    domains.append("('email_unauthorized','=', False)")

                if wizard.internal_instance_id:
                    domains.append("('int_instance_id','child_of', [%s])" % wizard.internal_instance_id.id)

                if wizard.bounce_counter != 0:
                    wizard.bounce_counter = wizard.bounce_counter if wizard.bounce_counter >= 0 else 0
                    domains.append("('email_bounce_counter','<=', %s)" % wizard.bounce_counter)

                context['more_filter'] = domains

                if wizard.e_mass_function == 'csv':
                    #
                    # Get CSV containing email coordinates
                    #
                    if wizard.sort_by:
                        context['sort_by'] = wizard.sort_by
                    if wizard.groupby_coresidency:
                        context['alternative_group_by'] = 'co_residency_id'

                    context['field_main_object'] = 'email_coordinate_id'
                    context['target_model'] = wizard.trg_model
                    active_ids, alternative_ids = self.pool['distribution.list'].get_complex_distribution_list_ids(cr, uid, [context.get('active_id', False)], context=context)
                    self.render_csv(cr, uid, wizard.trg_model, active_ids, context=context)

                elif wizard.e_mass_function == 'email_coordinate_id':
                    #
                    # Send mass mailing
                    #
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

                    active_ids, alternative_ids = self.pool['distribution.list'].get_complex_distribution_list_ids(cr, uid, [context.get('active_id', False)], context=context)
                    context['active_ids'] = active_ids
                    if alternative_ids and wizard.extract_csv:
                        self.render_csv(cr, uid, 'postal.coordinate', alternative_ids, wizard.groupby_coresidency, context=context)

                    self.pool['mail.compose.message'].send_mail(cr, uid, [mail_composer_id], context=context)

                elif wizard.e_mass_function == 'vcard':
                    context['field_main_object'] = 'email_coordinate_id'
                    context['target_model'] = wizard.trg_model
                    active_ids, alternative_ids = self.pool['distribution.list'].get_complex_distribution_list_ids(cr, uid, [context.get('active_id', False)], context=context)
                    self.export_vcard(cr, uid, active_ids, context)

            elif wizard.trg_model == 'postal.coordinate':
                domains = []

                if wizard.include_unauthorized:
                    domains.append("'|',('postal_unauthorized','=', True),('postal_unauthorized','=', False)")
                else:
                    domains.append("('postal_unauthorized','=', False)")

                if wizard.internal_instance_id:
                    domains.append("('int_instance_id','child_of', [%s])" % wizard.internal_instance_id.id)
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
                    active_ids, alternative_ids = self.pool['distribution.list'].get_complex_distribution_list_ids(cr, uid, [context.get('active_id', False)], context=context)
                    self.render_csv(cr, uid, wizard.trg_model, active_ids, context=context)

                    if wizard.postal_mail_id:
                        self._generate_postal_log(cr, uid, wizard.postal_mail_id.id, active_ids, context=context)

                if wizard.p_mass_function == 'postal_coordinate_id':
                    #
                    # Get postal coordinate labels PDF
                    #
                    context['more_filter'] = domains
                    context['field_main_object'] = 'postal_coordinate_id'
                    context['target_model'] = wizard.trg_model
                    active_ids, alternative_ids = self.pool['distribution.list'].get_complex_distribution_list_ids(cr, uid, [context.get('active_id', False)], context=context)

                    ctx = context.copy()
                    ctx.update({
                        'active_model': 'postal.coordinate',
                        'active_ids': active_ids,
                    })
                    report = self.pool['report'].get_pdf(cr, uid, active_ids, report_name='ficep_address.report_postal_coordinate_label', context=ctx)

                    if wizard.postal_mail_id:
                        self._generate_postal_log(cr, uid, wizard.postal_mail_id.id, active_ids, context=context)

                    attachment = [(_('Report.pdf'), '%s' % report)]
                    partner_ids = self.pool['res.partner'].search(cr, uid, [('user_ids', '=', uid)], context=context)
                    if partner_ids:
                        self.pool['mail.thread'].message_post(cr, uid, False, attachments=attachment, context=context, partner_ids=partner_ids, subject=_('Export PDF'))

    def _generate_postal_log(self, cr, uid, postal_mail_id, postal_coordinate_ids, context=None):
        """
        ====================
        _generate_postal_log
        ====================
        Generate a postal mail log for each coordinate for the specified postal mail.
        """
        if not context:
            context = {}

        postal_mail_log_obj = self.pool['postal.mail.log']
        now = datetime.now()

        for postal_coordinate_id in postal_coordinate_ids:
            postal_mail_log_obj.create(cr, uid, {
                'postal_mail_id': postal_mail_id,
                'postal_coordinate_id': postal_coordinate_id,
                'sent_date': now,
            }, context=context)

        self.pool['postal.mail'].write(cr, uid, postal_mail_id, {'sent_date': now}, context=context)

        return True

    def _get_csv_values(self, cr, uid, model, obj, context=None):
        """
        ===============
        _get_csv_values
        ===============
        Get the values of the specified obj, which should be an instance of the specified model.
        The model should be either an email or postal coordinate.
        """
        def safe_get(o, attr, default=None):
            try:
                return getattr(o, attr)
            except orm.except_orm:
                return default

        def _get_utf8(data):
            return data.encode('utf-8')

        # Test access coordinate (VIP READER)
        partner = safe_get(obj, 'partner_id')

        if not partner:
            return False

        # If we have a postal coordinate, we get the mail coordinates from the partner, and vice versa.
        if model == 'postal.coordinate':
            pc = obj
            ec = partner.email_coordinate_id
        elif model == 'email.coordinate':
            ec = obj
            pc = partner.postal_coordinate_id

        export_values = OrderedDict([('name', _get_utf8(partner.lastname)),
                                     ('lastname', None if not partner.usual_lastname else _get_utf8(partner.usual_lastname)),
                                     ('firstname', None if not partner.firstname else _get_utf8(partner.firstname)),
                                     ('usual_firstname', None if not partner.usual_firstname else _get_utf8(partner.usual_firstname)),
                                     ('identifier', partner.identifier or None),
                                     ('printable_name', _get_utf8(pc.co_residency_id.line) if (pc and pc.co_residency_id.line) \
                                         else _get_utf8(partner.printable_name)),
                                     ('co_residency', _get_utf8(pc.co_residency_id.line2) if (pc and pc.co_residency_id.line2) \
                                         else None),
                                     ('adr_main', pc and pc.is_main),
                                     ('adr_unauthorized', pc and pc.unauthorized),
                                     ('adr_vip', pc and pc.vip),
                                     ('country_code', pc and pc.address_id.country_code or None),
                                     ('country_name', _get_utf8(pc.address_id.country_id.name) if pc else None),
                                     ('zip', pc and pc.address_id.zip or None),
                                     ('street', None if not pc or not pc.address_id.street else _get_utf8(pc.address_id.street)),
                                     ('street2', None if not pc or not pc.address_id.street2 else _get_utf8(pc.address_id.street2)),
                                     ('city', None if not pc or pc.address_id.city else _get_utf8(pc.address_id.city)),
                                     ('instance', partner.int_instance_id and _get_utf8(partner.int_instance_id.name) or None),
                                     ('birth_date', partner.birth_date or None),
                                     ('gender', available_genders.get(partner.gender, None)),
                                     ('tongue', available_tongues.get(partner.tongue, None)),
                                     ('fix_main', partner.fix_coordinate_id and partner.fix_coordinate_id.is_main or False),
                                     ('fix_unauthorized', partner.fix_coordinate_id and partner.fix_coordinate_id.unauthorized or False),
                                     ('fix_vip', partner.fix_coordinate_id and partner.fix_coordinate_id.vip or False),
                                     ('fix', None if not partner.fix_coordinate_id else _get_utf8(partner.fix_coordinate_id.phone_id.name)),
                                     ('mobile_main', partner.mobile_coordinate_id and partner.mobile_coordinate_id.is_main or False),
                                     ('mobile_unauthorized', partner.mobile_coordinate_id and partner.mobile_coordinate_id.unauthorized or False),
                                     ('mobile_vip', partner.mobile_coordinate_id and partner.mobile_coordinate_id.vip or False),
                                     ('mobile', None if not partner.mobile_coordinate_id else _get_utf8(partner.mobile_coordinate_id.phone_id.name)),
                                     ('fax_main', partner.fax_coordinate_id and partner.fax_coordinate_id.is_main or False),
                                     ('fax_unauthorized', partner.fax_coordinate_id and partner.fax_coordinate_id.unauthorized or False),
                                     ('fax_vip', partner.fax_coordinate_id and partner.fax_coordinate_id.vip or False),
                                     ('fax', None if not partner.fax_coordinate_id else _get_utf8(partner.fax_coordinate_id.phone_id.name)),
                                     ('email_main', ec and ec.is_main or False),
                                     ('email_unauthorized', ec and ec.unauthorized or False),
                                     ('email_vip', ec and ec.vip or False),
                                     ('email', None if not partner.email_coordinate_id \
                                         else _get_utf8(partner.email_coordinate_id.email)),
                                     ])
        return export_values

    def render_csv(self, cr, uid, model, model_ids, group_by=False, context=None):
        """
        ==========
        render_csv
        ==========
        Get a CSV file with data of postal_ids depending of ``HEADER_ROW``
        Send  the CSV as message into the inbox of the user
        :type model_ids: []
        """

        if model not in ['postal.coordinate', 'email.coordinate']:
            return

        objects = self.pool[model].browse(cr, uid, model_ids, context=context)
        tmp = tempfile.NamedTemporaryFile(prefix='Extract', suffix=".csv", delete=False)
        f = open(tmp.name, "r+")
        writer = csv.writer(f)
        writer.writerow(HEADER_ROW)
        co_residencies = []
        for obj in objects:
            if model == 'postal.coordinate':
                #case group by is ask and where a co_residency is present and already write then don't write a new row
                if group_by and obj.co_residency_id and obj.co_residency_id.id in co_residencies:
                    continue
                co_residencies.append(obj.co_residency_id.id)

            export_values = self._get_csv_values(cr, uid, model, obj)
            if not export_values:
                continue

            writer.writerow(export_values.values())
        f.close()
        f = open(tmp.name, "r")
        attachment = [(_('Extract.csv'), '%s' % f.read())]
        partner_ids = self.pool['res.partner'].search(cr, uid, [('user_ids', '=', uid)], context=context)
        if partner_ids:
            self.pool['mail.thread'].message_post(cr, uid, False, attachments=attachment, context=context, partner_ids=partner_ids, subject=_('Export CSV'))

    def export_vcard(self, cr, uid, email_coordinate_ids, context=None):
        """
        ============
        export_vcard
        ============
        Export the specified coordinates to a VCF file.
        :type email_coordinate_ids: []
        """
        tmp = tempfile.NamedTemporaryFile(prefix='vCard', suffix=".vcf", delete=False)
        f = codecs.open(tmp.name, "r+", "utf-8")

        def safe_get(o, attr, default=None):
            try:
                return getattr(o, attr)
            except orm.except_orm:
                return default

        def _get_unicode(data):
            return data and unicode(data) or False

        for ec in self.pool['email.coordinate'].browse(cr, uid, email_coordinate_ids):
            partner = safe_get(ec, 'partner_id')
            if not partner:
                continue

            card = vobject.vCard()
            card.add('fn').value = _get_unicode(partner.printable_name)
            if not partner.usual_lastname and not partner.firstname:
                card.add('n').value = vobject.vcard.Name(_get_unicode(partner.printable_name))
            else:
                card.add('n').value = vobject.vcard.Name(_get_unicode(partner.usual_lastname) or _get_unicode(partner.lastname) or '', _get_unicode(partner.firstname))

            emailpart = card.add('email')
            emailpart.value = _get_unicode(ec.email)
            emailpart.type_param = 'INTERNET'

            if partner.fix_coordinate_id and partner.fix_coordinate_id.phone_id:
                fix_part = card.add('tel')
                fix_part.type_param = 'WORK'
                fix_part.value = partner.fix_coordinate_id.phone_id.name

            if partner.mobile_coordinate_id and partner.mobile_coordinate_id.phone_id:
                fix_part = card.add('tel')
                fix_part.type_param = 'CELL'
                fix_part.value = partner.mobile_coordinate_id.phone_id.name

            # CHEKME: add more informations? http://www.evenx.com/vcard-3-0-format-specification
            # TODO: verify and fix utf-8 encoding

            f.write(card.serialize().decode('utf-8'))

        f.close()
        f = open(tmp.name, "r")
        attachment = [(_('Extract.vcf'), '%s' % f.read())]
        partner_ids = self.pool['res.partner'].search(cr, uid, [('user_ids', '=', uid)], context=context)
        if partner_ids:
            self.pool['mail.thread'].message_post(cr, uid, False, attachments=attachment, context=context, partner_ids=partner_ids, subject=_('Export VCF'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
