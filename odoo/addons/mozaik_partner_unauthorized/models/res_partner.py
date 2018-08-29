# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from operator import attrgetter

from odoo import api, fields, models

TRIGGER_UNAUTHORIZED = [
    'email_coordinate_id',
    'postal_coordinate_id',
    'fix_coordinate_id',
    'fax_coordinate_id',
    'mobile_coordinate_id'
]


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.one
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
        for f in TRIGGER_UNAUTHORIZED:
            if attrgetter('%s.unauthorized' % f)(self):
                self.unauthorized = True
                break

    unauthorized = fields.Boolean(
        compute='_compute_unauthorized',
        store=True,
        help='Checked if one or more main coordinates are unauthorized',
    )
