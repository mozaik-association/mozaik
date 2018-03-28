# -*- coding: utf-8 -*-
# © 2018 ACSONE SA/NV <https://acsone.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models, _
try:
    from openerp.exceptions import UserError
except ImportError:
    from openerp.exceptions import Warning as UserError


class EmailTemplate(models.Model):
    _inherit = 'email.template'

    # Fake field for auto-completing placeholder
    involvement_category_id = fields.Many2one(
        'partner.involvement.category', string='Involvement Category',
        domain=[('code', '!=', False)])

    @api.onchange('placeholder_id')
    def _onchange_placeholder_id(self):
        super(EmailTemplate, self)._onchange_placeholder_id()
        for wizard in self:
            placeholder_value = wizard.placeholder_value
            if placeholder_value and '{{CODE}}' in placeholder_value:
                if not wizard.involvement_category_id:
                    raise UserError(_(
                        'Please select an involvement category'))
                placeholder_value = placeholder_value.replace(
                    '{{CODE}}', wizard.involvement_category_id.code)
                wizard.placeholder_value = placeholder_value
