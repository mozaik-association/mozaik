# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class PrintPostalFromPartnerWizard(models.TransientModel):

    _name = 'print.postal.from.partner.wizard'
    _description = 'Print Postal From Partner Wizard'

    @api.multi
    def print_postal_from_partner_button(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        ctx['active_model'] = 'postal.coordinate'
        partner_ids = ctx.get('active_ids')
        domain = [
            ('is_main', '=', True),
            ('partner_id', 'in', partner_ids),
        ]
        postal_ids = self.env['postal.coordinate'].search(domain)
        ctx['active_ids'] = postal_ids.ids
        return self.pool['report'].get_action(
            self.env.cr, self.env.uid, [],
            'mozaik_address.report_postal_coordinate_label',
            data={'report_type': 'qweb-pdf'}, context=ctx)
