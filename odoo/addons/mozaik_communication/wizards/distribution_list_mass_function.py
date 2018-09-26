# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import random
from email.utils import formataddr
from odoo import api, exceptions, models, fields, _


class DistributionListMassFunction(models.TransientModel):
    _name = 'distribution.list.mass.function'
    _description = 'Mass Function'

    @api.model
    def _get_e_mass_function(self):
        """
        Get available mass functions for mode=email.coordinate
        :return:
        """
        funcs = [
            ('email_coordinate_id', _('Mass Mailing')),
            ('csv', _('CSV Extraction')),
        ]
        return funcs

    @api.model
    def _get_default_e_mass_function(self):
        """
        Get default email.coordinate mass function
        :return:
        """
        funcs = self._get_e_mass_function()
        return funcs[0][0]

    trg_model = fields.Selection(
        selection=[
            ('email.coordinate', 'Email Coordinate'),
            ('postal.coordinate', 'Postal Coordinate'),
        ],
        string="Sending mode",
        required=True,
        default='email.coordinate',
    )
    e_mass_function = fields.Selection(
        selection=_get_e_mass_function,
        string="Mass function",
        default=lambda self: self._get_default_e_mass_function(),
    )
    p_mass_function = fields.Selection(
        selection=[
            ('csv', 'CSV Extraction'),
        ],
        string="Mass function",
        default="csv",
    )
    distribution_list_id = fields.Many2one(
        comodel_name="distribution.list",
        string="Distribution list",
        required=True,
        ondelete="cascade",
        default=lambda self: self.env.context.get('active_id', False),
    )
    subject = fields.Char()
    body = fields.Html(
        string="Content",
        help="Automatically sanitized HTML contents",
    )
    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        relation="distribution_list_mass_function_ir_attachment_rel",
        column1="wizard_id",
        column2="attachment_id",
        string="Attachments",
    )
    mass_mailing_name = fields.Char()
    extract_csv = fields.Boolean(
        string="Complementary postal CSV",
        help="Get a CSV file for partners without email",
        default=False,
    )
    postal_mail_name = fields.Char()
    sort_by = fields.Selection(
        selection=[
            ('identifier', 'Identification Number'),
            ('technical_name', 'Name'),
            ('country_id, zip, technical_name', 'Zip Code'),
        ],
    )
    bounce_counter = fields.Integer(
        string="Maximum of fails",
    )
    include_unauthorized = fields.Boolean(
        default=False,
    )
    internal_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="Internal instance",
        ondelete="cascade",
    )
    include_without_coordinate = fields.Boolean(
        default=False,
    )
    groupby_coresidency = fields.Boolean(
        string="Group by co-residency",
        default=False,
    )
    export_file = fields.Binary(
        string="File",
        readonly=True,
    )
    export_filename = fields.Char(
    )
    # Fake field for auto-completing placeholder
    placeholder_id = fields.Many2one(
        comodel_name='email.template.placeholder',
        string="Placeholder",
        domain=[('model_id', '=', 'email.coordinate')],
    )
    placeholder_value = fields.Char(
        help="Copy this text to the email body. It'll be replaced by the "
             "value from the document",
    )
    involvement_category_id = fields.Many2one(
        comodel_name='partner.involvement.category',
        string='Involvement Category',
        domain=[('code', '!=', False)],
    )
    contact_ab_pc = fields.Integer(
        string='AB Batch (%)',
        default=100,
    )
    partner_from_id = fields.Many2one(
        comodel_name='res.partner',
        string='From',
        domain=lambda self: self._get_domain_partner_from_id(),
        default=lambda self: self._get_default_partner_from_id(),
        context={'show_email': 1},
    )
    partner_name = fields.Char(
    )
    email_from = fields.Char(
        readonly=True,
    )
    mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Email Template',
    )

    @api.onchange("trg_model")
    def _onchange_trg_model(self):
        """
        Reset some fields when `trg_model` change
        """
        if self.trg_model == 'postal.coordinate':
            self.e_mass_function = False
            self.p_mass_function = self._fields[
                'p_mass_function'].selection[0][0]
        if self.trg_model == 'email.coordinate':
            self.e_mass_function = self._get_default_e_mass_function()
            self.p_mass_function = False

    @api.onchange("e_mass_function")
    def _onchange_e_mass_function(self):
        """
        Reset some fields when `mass_function` change
        """
        self.extract_csv = False
        self.export_filename = False
        self.include_without_coordinate = False

    @api.onchange("subject")
    def _onchange_subject(self):
        """
        Propose a default value for the mass mailing name
        """
        if not self.mass_mailing_name:
            self.mass_mailing_name = self.subject

    @api.multi
    def mass_function(self):
        """
        This method allow to make mass function on
        - email.coordinate
        - postal.coordinate
        """
        self.ensure_one()
        context = self.env.context.copy()
        main_domain = []
        if self.internal_instance_id:
            main_domain.append(
                ('int_instance_id', 'child_of', self.internal_instance_id.ids)
            )
        context.update({
            'main_object_domain': main_domain,
        })
        fct = self.e_mass_function
        if self.trg_model != 'email.coordinate':
            fct = self.p_mass_function
        if (fct == 'csv' or self.extract_csv) \
                and self.include_without_coordinate:
            context.update({
                'active_test': False,
                'alternative_object_field': 'id',
                'alternative_target_model':
                    self.distribution_list_id.dst_model_id.model,
                'alternative_object_domain': main_domain,
            })
        if self.sort_by:
            context.update({
                'sort_by': self.sort_by,
            })

        csv_model = self.trg_model
        self_ctx = self.with_context(context)
        if self.trg_model == 'email.coordinate':
            alternatives, mains = self_ctx._mass_email_coordinate(
                fct, main_domain)
            if alternatives and self.extract_csv:
                fct = 'csv'
                csv_model = 'postal.coordinate'
                mains = alternatives
        elif self.trg_model == 'postal.coordinate':
            alternatives, mains = self_ctx._mass_postal_coordinate(
                fct, main_domain)

        if fct == 'csv':
            if self.include_without_coordinate:
                self.export_csv('virtual.target', alternatives)
            else:
                self.export_csv(csv_model, mains, self.groupby_coresidency)

            return {
                'name': _('Mass Function'),
                'type': 'ir.actions.act_window',
                'res_model': 'distribution.list.mass.function',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }
        return {}

    @api.multi
    def _mass_postal_coordinate(self, fct, main_domain):
        """
        Manage mass function when the target model is postal.coordinate
        :param fct: str
        :param main_domain: list (domain)
        :return: tuple of 2 recordset
        """
        if not self.include_unauthorized:
            main_domain.append(('postal_unauthorized', '=', False))
        if self.bounce_counter:
            bounce_counter = max([self.bounce_counter, 0])
            main_domain.append(('postal_bounce_counter', '<=', bounce_counter))
        self = self.with_context(
            main_object_field='postal_coordinate_id',
            main_target_model='postal.coordinate',
        )
        if fct == 'csv':
            # Get CSV containing postal coordinates
            dl = self.distribution_list_id
            mains, alternatives = dl._get_complex_distribution_list_ids()

            if self.postal_mail_name and not self.include_without_coordinate:
                self._post_processing(mains)
                self.env['postal.mail']._generate_postal_log(
                    self.postal_mail_name, mains)
        return alternatives, mains

    @api.multi
    def _mass_email_coordinate(self, fct, main_domain):
        """
        Manage mass function when the target model is email.coordinate
        :param fct: str
        :param main_domain: list (domain)
        :return: tuple of 2 recordset
        """
        context = self._context
        if self.distribution_list_id.dst_model_id.model == 'virtual.target':
            if not self.include_unauthorized:
                main_domain.append(('email_unauthorized', '=', False))
            if self.bounce_counter:
                bounce_counter = max([self.bounce_counter, 0])
                main_domain.append(
                    ('email_bounce_counter', '<=', bounce_counter))
        self = self.with_context(
            main_object_field='email_coordinate_id',
            main_target_model='email.coordinate',
        )
        if fct == 'csv':
            # Get CSV containing email coordinates
            dl = self.distribution_list_id
            mains, alternatives = dl._get_complex_distribution_list_ids()

        elif fct == 'email_coordinate_id':
            if self.extract_csv:
                if not self.include_without_coordinate:
                    self = self.with_context(
                        alternative_object_field='postal_coordinate_id',
                        alternative_target_model='postal.coordinate',
                        alternative_object_domain=[
                            ('email_coordinate_id', '=', False),
                        ],
                    )
            dl = self.distribution_list_id
            mains, alternatives = dl._get_complex_distribution_list_ids()

            if self.contact_ab_pc < 100 or context.get('mailing_group_id'):
                if context.get('mailing_group_id'):
                    stats_obj = self.env['mail.mail.statistics']
                    domain = [
                        ('mass_mailing_id.group_id', '=',
                         context.get('mailing_group_id')),
                    ]
                    stats = stats_obj.search(domain)
                    already_mailed = stats.mapped("res_id")
                    remaining = set(mains).difference(already_mailed)
                else:
                    group_obj = self.env['mail.mass_mailing.group']
                    new_group = group_obj.create({
                        'distribution_list_id': dl.id,
                        'include_unauthorized': self.include_unauthorized,
                        'internal_instance_id': self.internal_instance_id.id,
                    })
                    context.update({
                        'mailing_group_id': new_group.id,
                    })
                    remaining = mains
                topick = int(len(mains) / 100.0 * self.contact_ab_pc)
                if topick > len(remaining):
                    topick = len(remaining)
                mains = random.sample(remaining, topick)

            if self.extract_csv and alternatives:
                if self.postal_mail_name and \
                        not self.include_without_coordinate:
                    self.env['postal.mail']._generate_postal_log(
                        self.postal_mail_name, alternatives)
            elif not mains:
                raise exceptions.UserError(_('There are no recipients'))
            self = self.with_context(
                active_ids=mains.ids,
                async_send_mail=True,
                dl_computed=True,
            )
            # Send mass mailing
            mail_composer = self._create_mail_composer()
            mail_composer.send_mail()

            if self.mass_mailing_name:
                self._post_processing(mains)
        return alternatives, mains

    def _create_mail_composer(self):
        """
        Create the mail.compose.message
        :return: mail.compose.message recordset
        """
        model = self.trg_model
        composer_obj = self.env['mail.compose.message']
        mail_composer_vals = {
            'email_from': self.email_from,
            'parent_id': False,
            'use_active_domain': False,
            'composition_mode': 'mass_mail',
            'partner_ids': [[6, False, []]],
            'notify': False,
            'template_id': self.mail_template_id.id,
            'subject': self.subject,
            'distribution_list_id': self.distribution_list_id.id,
            'mass_mailing_name': self.mass_mailing_name,
            'model': model,
            'body': self.body,
            'contact_ab_pc': self.contact_ab_pc,
        }
        attachments = self.attachment_ids.ids or []
        if self.mail_template_id:
            value = composer_obj.onchange_template_id(
                self.mail_template_id.id, 'mass_mail', '', 0).get('value', {})
            attachments += value.get('attachment_ids', [])
            for fld in ['subject', 'body', 'email_from']:
                value.pop(fld, None)
            mail_composer_vals.update(value)
        if attachments:
            mail_composer_vals.update({
                'attachment_ids': [(6, False, attachments)],
            })
        return composer_obj.create(mail_composer_vals)

    def export_csv(self, model, targets, group_by=False):
        """
        Export the specified coordinates to a CSV file.
        :param model: str
        :param targets: recordset
        :param group_by: bool
        :return: bool
        """
        csv_content = self.env['export.csv'].get_csv(
            model, targets, group_by=group_by)
        csv_content = base64.encodebytes(csv_content.encode())
        return self.write({
            'export_file': csv_content,
            'export_filename': 'extract.csv',
        })

    def _post_processing(self, records):
        """

        :param records: recordset
        :return: bool
        """
        return True

    @api.model
    def _get_partner_from(self):
        """
        Get partner from distribution list
        :return: res.partner recordset
        """
        partners = self.env['res.partner'].browse()
        model = self.env.context.get('active_model')
        dist_list = False
        if self.env.context.get('active_id'):
            dist_list = self.env[model].browse(self.env.context['active_id'])
        if dist_list and model == self._name:
            # in case of wizard reloading
            dist_list = dist_list.distribution_list_id
        if dist_list:
            # first: the sender partner
            partners |= dist_list.partner_id
            # than: the requestor user
            if self.env.user.partner_id in dist_list.res_partner_ids:
                partners |= self.env.user.partner_id
            elif self.env.user in dist_list.res_users_ids:
                partners |= self.env.user.partner_id
            # finally: all owners and allowed partners that are legal persons
            partners |= dist_list.res_partner_ids.filtered(
                lambda s: s.is_company)
            partners |= dist_list.res_users_ids.mapped(
                'partner_id').filtered(lambda s: s.is_company)
        return partners.filtered(lambda s: s.email)

    @api.model
    def _get_domain_partner_from_id(self):
        """
        Load partners and transform results into a domain
        :return: list (domain)
        """
        partners = self._get_partner_from()
        return [('id', 'in', partners.ids)]

    @api.model
    def _get_default_partner_from_id(self):
        """

        :return: res.partner recordset
        """
        if self.env.user.partner_id in self._get_partner_from():
            return self.env.user.partner_id
        return self.env['res.partner'].browse()

    @api.onchange('partner_from_id', 'partner_name')
    def _onchange_partner_from(self):
        self.ensure_one()
        name = ''
        email = ''
        if self.partner_from_id:
            name = self.partner_from_id.name
            email = self.partner_from_id.email or ''
        if self.partner_name:
            name = self.partner_name.strip()
        self.email_from = formataddr((name, email))

    @api.onchange('mail_template_id')
    def _onchange_template_id(self):
        """
        Instanciate subject and body from template to wizard
        """
        tmpl = self.mail_template_id
        if tmpl:
            if tmpl.subject:
                self.subject = tmpl.subject
            if tmpl.body_html:
                self.body = tmpl.body_html

    @api.onchange('placeholder_id', 'involvement_category_id')
    def _onchange_placeholder_id(self):
        code_key = '{{CODE}}'
        for wizard in self:
            if wizard.placeholder_id:
                placeholder_value = wizard.placeholder_id.placeholder
                wizard.placeholder_id = False
                if code_key in placeholder_value \
                        and wizard.involvement_category_id:
                    placeholder_value = placeholder_value.replace(
                        code_key, wizard.involvement_category_id.code)
                wizard.placeholder_value = placeholder_value

    @api.multi
    def save_as_template(self):
        self.ensure_one()
        template_name = u"Mass Function: {subject}"
        values = {
            'name': template_name.format(subject=self.subject),
            'subject': self.subject or False,
            'body_html': self.body or False,
        }
        template = self.env['mail.template'].create(values)
        self.mail_template_id = template
        self._onchange_template_id()

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'res_model': self._name,
            'target': 'new',
            'context': self.env.context,
        }
