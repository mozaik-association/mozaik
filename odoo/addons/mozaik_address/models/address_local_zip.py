# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AddressLocalZip(models.Model):

    _name = 'address.local.zip'
    _inherit = ['mozaik.abstract.model']
    _description = 'Local Zip Code'

    @api.multi
    def _get_linked_addresses(self):
        return self.env['address.address'].search(
            [('address_local_zip_id', 'in', self._ids)])

    local_zip = fields.Char(
        string='Zip Code', required=True, index=True,
        track_visibility='onchange')
    town = fields.Char(
        required=True, index=True, track_visibility='onchange')
    sequence = fields.Integer(default=16)

    _rec_name = 'local_zip'

    _order = "local_zip, sequence, town"

    _unicity_keys = 'local_zip, town'

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = "%s %s" % (record.local_zip, record.town)
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        dom = args + [
            '|',
            ('local_zip', operator, name),
            ('town', operator, name)
        ]
        return self.search(dom, limit=limit).name_get()

    @api.multi
    def get_linked_partners(self):
        adr_ids = self._get_linked_addresses()
        return adr_ids.get_linked_partners()
