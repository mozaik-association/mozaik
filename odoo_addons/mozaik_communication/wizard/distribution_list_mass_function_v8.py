# -*- coding: utf-8 -*-
# © 2018 ACSONE SA/NV <https://acsone.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class DistributionListMassFunction(models.TransientModel):
    _inherit = 'distribution.list.mass.function'

    @api.multi
    def save_as_template(self):
        template_name = u"Mass Function: {subject}"
        model = self.env['ir.model'].search(
            [('model', '=', 'email.coordinate')], limit=1)
        for record in self:
            values = {
                'name': template_name.format(subject=record.subject),
                'subject': record.subject or False,
                'body_html': record.body or False,
                'model_id': model.id,
            }
            template = self.env['email.template'].create(values)
            new_values = record.onchange_template_id(template.id)['value']
            new_values['email_template_id'] = template.id
            record.write(new_values)

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': record.id,
            'res_model': 'email.coordinate',
            'target': 'new',
            'context': dict(self.env.context),
        }
