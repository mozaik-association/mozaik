# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class ChangeMainAddress(models.TransientModel):

    _name = 'change.main.address'
    _inherit = 'change.main.coordinate'
    _description = 'Change Main Address Wizard'

    old_address_id = fields.Many2one(
        'address.address', 'Current Main Address')
    address_id = fields.Many2one(
        'address.address', 'New Main Address',
        required=True, ondelete='cascade')
    co_residency_id = fields.Many2one('co.residency', 'Co-Residency')
    move_co_residency = fields.Boolean('Move Co-Residency', default=True)
    invalidate_co_residency = fields.Boolean('Invalidate Co-Residency',
                                             default=True)
    move_allowed = fields.Boolean(readonly=True)
    message = fields.Char()

    @api.model
    def default_get(self, fields_list):
        context = self.env.context
        res = super().default_get(fields_list)
        if context.get('mode', False) == 'switch':
            coord = self.env[self._get_target_model()].browse(
                context.get('active_id', False))
            res['address_id'] = coord.address_id.id
        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []
        if len(ids) == 1:
            partner = self.env['res.partner'].sudo().browse(ids[0])
            res['old_address_id'] = partner.postal_coordinate_id.address_id.id
            if context.get('address_id', False):
                res['change_allowed'] = not(
                    res['address_id'] == res['old_address_id'])
            if res.get('old_address_id', False):
                cores_obj = self.env['co.residency']
                cores_wiz_obj = self.env['change.co.residency.address']
                co_res = cores_obj.search(
                    [('address_id', '=', res['old_address_id'])])
                if co_res:
                    co_res_id = co_res[0].id
                    if co_res_id:
                        res['move_allowed'] = cores_wiz_obj._use_allowed(
                            co_res_id)
                    res['co_residency_id'] = co_res_id
                    res['move_co_residency'] = res.get('move_allowed', False)
                    res['invalidate_co_residency'] = res.get('move_allowed',
                                                             False)
                    if not res.get('move_allowed', False):
                        res['message'] = _('Due to security restrictions'
                                           ' you are not allowed to move'
                                           ' all co-residency members !')
            res['address_id'] = res['old_address_id']
        return res

    @api.multi
    def button_change_main_coordinate(self):
        postal_coordinate_ids = False
        if self.co_residency_id and self.move_co_residency:
            postal_coordinate_ids = self.co_residency_id.postal_coordinate_ids
            cores_wiz_obj = self.env['change.co.residency.address']
            vals = {
                'co_residency_id': self.co_residency_id.id,
                'old_address_id': self.old_address_id.id,
                'address_id': self.address_id.id,
                'use_allowed': self.move_allowed,
                'invalidate': self.invalidate_co_residency,
            }
            wizard = cores_wiz_obj.create(vals)
            wizard.change_address()
        res = super().button_change_main_coordinate()
        if self.invalidate_previous_coordinate and postal_coordinate_ids:
            postal_coordinate_ids.action_invalidate()
        return res
