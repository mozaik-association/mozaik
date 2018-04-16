# -*- coding: utf-8 -*-
# © 2018 ACSONE SA/NV <https://acsone.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class DistributionListMassFunction(models.TransientModel):
    _inherit = 'distribution.list.mass.function'

    # Fake field for auto-completing placeholder
    placeholder_id = fields.Many2one(
        'email.template.placeholder', string="Placeholder",
        domain=[('model_id', '=', 'email.coordinate')])
    placeholder_value = fields.Char(
        help="Copy this text to the email body. "
             "It'll be replaced by the value from the document")

    @api.onchange('placeholder_id')
    def _onchange_placeholder_id(self):
        for wizard in self:
            if wizard.placeholder_id:
                wizard.placeholder_value = wizard.placeholder_id.placeholder
                wizard.placeholder_id = False

    @api.multi
    def save_as_template(self):
        self.ensure_one()
        template_name = u"Mass Function: {subject}"
        model = self.env['ir.model'].search(
            [('model', '=', 'email.coordinate')], limit=1)
        values = {
            'name': template_name.format(subject=self.subject),
            'subject': self.subject or False,
            'body_html': self.body or False,
            'model_id': model.id,
        }
        template = self.env['email.template'].create(values)
        new_values = self.onchange_template_id(template.id)['value']
        new_values['email_template_id'] = template.id
        self.write(new_values)

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'res_model': self._name,
            'target': 'new',
            'context': dict(self.env.context),
        }
