# -*- coding: utf-8 -*-
# © 2018 ACSONE SA/NV <https://acsone.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models
from email.utils import formataddr


class DistributionListMassFunction(models.TransientModel):
    _inherit = 'distribution.list.mass.function'

    @api.model
    def _get_partner_from(self):
        pids = self.env['res.partner']
        model = self._context.get('active_model')
        active_id = self._context.get('active_id') or False
        dl = active_id and self.env[model].browse([active_id]) or False
        if dl and model == self._name:
            # in case of wizard reloading
            dl = dl.distribution_list_id
        if dl:
            # first: the sender partner
            if dl.partner_id:
                pids |= dl.partner_id
            # than: the requestor user
            if self.env.user.partner_id in dl.res_partner_m2m_ids:
                pids |= self.env.user.partner_id
            elif self.env.user in dl.res_users_ids:
                pids |= self.env.user.partner_id
            # finally: all owners and allowed partners that are legal persons
            pids |= dl.res_partner_m2m_ids.filtered(lambda s: s.is_company)
            u_pids = dl.res_users_ids.mapped('partner_id')
            # re-search them to apply security rules
            u_pids = self.env['res.partner'].search([('id', 'in', u_pids.ids)])
            if u_pids:
                pids |= u_pids.filtered(lambda s: s.is_company)
        return pids.filtered(lambda s: s.email)

    @api.model
    def _get_domain_partner_from_id(self):
        partners = self._get_partner_from()
        return [('id', 'in', partners.ids)]

    @api.model
    def _get_default_partner_from_id(self):
        if self.env.user.partner_id in self._get_partner_from():
            return self.env.user.partner_id
        return False

    # Fake field for auto-completing placeholder
    placeholder_id = fields.Many2one(
        'email.template.placeholder', string="Placeholder",
        domain=[('model_id', '=', 'email.coordinate')])
    placeholder_value = fields.Char(
        help="Copy this text to the email body. "
             "It'll be replaced by the value from the document")
    involvement_category_id = fields.Many2one(
        'partner.involvement.category', string='Involvement Category',
        domain=[('code', '!=', False)])
    contact_ab_pc = fields.Integer('AB Batch (%)', default=100)
    partner_from_id = fields.Many2one(
        'res.partner', string='From',
        domain=lambda s: s._get_domain_partner_from_id(),
        default=lambda s: s._get_default_partner_from_id(),
        context={'show_email': 1})
    partner_name = fields.Char()
    email_from = fields.Char(readonly=True)
    email_template_id = fields.Many2one(
        'email.template', string='Email Template')

    @api.onchange('partner_from_id', 'partner_name')
    def _onchange_partner_from(self):
        self.ensure_one()
        name = ''
        email = ''
        if self.partner_from_id:
            name = self.partner_from_id.name
            email = self.partner_from_id.email or ''
        if self.partner_name:
            name = self.partner_name and self.partner_name.strip() or name
        self.email_from = formataddr((name, email))

    @api.onchange('email_template_id')
    def _onchange_template_id(self):
        """
        Instanciate subject and body from template to wizard
        """
        tmpl = self.email_template_id
        if tmpl:
            if tmpl.subject:
                self.subject = tmpl.subject
            if tmpl.body_html:
                self.body = tmpl.body_html

    @api.onchange('placeholder_id', 'involvement_category_id')
    def _onchange_placeholder_id(self):
        for wizard in self:
            if wizard.placeholder_id:
                placeholder_value = wizard.placeholder_id.placeholder
                if '{{CODE}}' in placeholder_value \
                   and wizard.involvement_category_id:
                    placeholder_value = placeholder_value.replace(
                        '{{CODE}}', wizard.involvement_category_id.code)
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
        template = self.env['email.template'].create(values)
        self.email_template_id = template
        self._onchange_template_id()

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'res_model': self._name,
            'target': 'new',
            'context': dict(self.env.context),
        }
