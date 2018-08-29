# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

TRIGGER_UNAUTHORIZED = [
    'email_coordinate_id',
    'postal_coordinate_id',
    'fix_coordinate_id',
    'mobile_coordinate_id',
    'fax_coordinate_id',
]


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.multi
    @api.depends(
        'postal_coordinate_ids.unauthorized',
        'email_coordinate_ids.unauthorized',
        'phone_coordinate_ids.unauthorized',
        'postal_coordinate_ids.is_main',
        'email_coordinate_ids.is_main',
        'phone_coordinate_ids.is_main',
        'postal_coordinate_ids.active',
        'email_coordinate_ids.active',
        'phone_coordinate_ids.active')
    def _compute_unauthorized(self):
        for partner in self:
            unauthorized = False
            for f in TRIGGER_UNAUTHORIZED:
                if partner[f]['unauthorized']:
                    unauthorized = True
                    break
            partner.unauthorized = unauthorized

    unauthorized = fields.Boolean(
        compute='_compute_unauthorized',
        store=True,
        help='Checked if at least one main coordinate is unauthorized',
    )
