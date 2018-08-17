# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
from odoo.fields import first


class ChangeCoResidencyAddress(models.TransientModel):

    _name = 'change.co.residency.address'
    _description = 'Change Co-Residency Address Wizard'

    co_residency_id = fields.Many2one('co.residency', 'Co-Residency')
    old_address_id = fields.Many2one(
        'address.address', 'Current Address')
    address_id = fields.Many2one(
        'address.address', 'New Address',
        required=True, ondelete='cascade')
    use_allowed = fields.Boolean()
    invalidate = fields.Boolean('Invalidate Co-Residency', default=True)
    message = fields.Char()

    @api.model
    def _use_allowed(self, co_residency_id):
        co_res_obj = self.env['co.residency']
        sudo_res = co_res_obj.sudo().browse(co_residency_id)
        uid_res = co_res_obj.browse(co_residency_id)

        if (len(sudo_res.postal_coordinate_ids) !=
                len(uid_res.postal_coordinate_ids)):
            return False
        return True

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        ids = self.env.context.get('active_ids') \
            or (self.env.context.get('active_id') and
                [self.env.context.get('active_id')]) \
            or []
        if len(ids) == 1:
            if 'co_residency_id' in fields_list:
                res['co_residency_id'] = ids[0]

            if 'use_allowed' in fields_list:
                res['use_allowed'] = self._use_allowed(ids[0])
            if 'old_address_id' in fields_list:
                resid = self.env['co.residency'].browse(ids[0])
                res['old_address_id'] = resid.address_id.id
                res['invalidate'] = True

        return res

    @api.multi
    def change_address(self):
        self.ensure_one()
        co_res_obj = self.env['co.residency']
        coord_obj = self.env['postal.coordinate']
        dupl_wiz_obj = self.env['allow.duplicate.address.wizard']

        cores = co_res_obj.browse(self.co_residency_id.id)

        new_coord_ids = coord_obj.browse()
        for coord in cores.postal_coordinate_ids:
            if coord.is_main:
                pc_ids = coord_obj._change_main_coordinate(
                    coord.partner_id, self.address_id.id)
            else:
                domain = [('partner_id', '=', coord.partner_id.id),
                          ('address_id', '=', self.address_id.id)]
                pc_ids = coord_obj.search(domain)
                vals = dict(
                    partner_id=coord.partner_id.id,
                    address_id=self.address_id.id,
                    vip=coord.vip,
                    unauthorized=coord.unauthorized,
                    coordinate_category_id=coord.coordinate_category_id.id,
                    coordinate_type=coord.coordinate_type,
                    is_main=coord.is_main)
                if not pc_ids:
                    pc_ids = coord_obj.create(vals)
            if pc_ids:
                new_coord_ids += pc_ids
        if self.invalidate:
            postal_coordinate_id = cores.postal_coordinate_ids
            if postal_coordinate_id:
                first(postal_coordinate_id).button_undo_allow_duplicate()
            cores.action_invalidate()

        if new_coord_ids:
            dupl_wiz_id = dupl_wiz_obj.with_context(
                active_model=coord_obj._name,
                active_ids=new_coord_ids.ids,
                active_id=new_coord_ids[0].id,).create({})
            res = dupl_wiz_id.button_allow_duplicate()
            if res and res.get('new_co_res') and cores.line or cores.line2:
                new_cor_id = co_res_obj.browse(res['res_id'])
                vals = dict(line=cores.line,
                            line2=cores.line2)
                new_cor_id.write(vals)
            return res
        return False
