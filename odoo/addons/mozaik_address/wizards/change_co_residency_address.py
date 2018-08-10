# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID


class change_co_residency_address(orm.TransientModel):

    _name = 'change.co.residency.address'
    _description = 'Change Co-Residency Address Wizard'

    _columns = {
        'co_residency_id': fields.many2one('co.residency', 'Co-Residency'),
        'old_address_id': fields.many2one(
            'address.address', 'Current Address'),
        'address_id': fields.many2one(
            'address.address', 'New Address',
            required=True, ondelete='cascade'),
        'use_allowed': fields.boolean('Use allowed'),
        'invalidate': fields.boolean('Invalidate Co-Residency'),
        'message': fields.char('Message'),
    }

    _defaults = {
        'invalidate': True,
    }

    def _use_allowed(self, cr, uid, co_residency_id, context=None):
        co_res_obj = self.pool.get('co.residency')
        sudo_res = co_res_obj.browse(cr,
                                     SUPERUSER_ID,
                                     co_residency_id,
                                     context=context)
        uid_res = co_res_obj.browse(cr,
                                    uid,
                                    co_residency_id,
                                    context=context)

        if (len(sudo_res.postal_coordinate_ids) !=
           len(uid_res.postal_coordinate_ids)):
            return False
        return True

    def default_get(self, cr, uid, flds, context):
        res = {}
        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []
        if len(ids) == 1:
            if 'co_residency_id' in flds:
                res['co_residency_id'] = ids[0]

            if 'use_allowed' in flds:
                res['use_allowed'] = self._use_allowed(cr,
                                                       uid,
                                                       ids[0],
                                                       context=context)
            if 'old_address_id' in flds:
                resid = self.pool.get('co.residency').browse(
                    cr, uid, ids[0], context=context)
                res['old_address_id'] = resid.address_id.id
                res['invalidate'] = True

        return res

    def change_address(self, cr, uid, ids, context=None):
        wiz = self.browse(cr, uid, ids[0], context=context)
        co_res_obj = self.pool['co.residency']
        coord_obj = self.pool['postal.coordinate']
        dupl_wiz_obj = self.pool['allow.duplicate.address.wizard']

        cores = co_res_obj.browse(cr,
                                  uid,
                                  wiz.co_residency_id.id,
                                  context=context)

        new_coord_ids = []
        for coord in cores.postal_coordinate_ids:
            if coord.is_main:
                pc_ids = coord_obj._change_main_coordinate(
                    cr,
                    uid,
                    [coord.partner_id.id],
                    wiz.address_id.id,
                    context=context)
            else:
                domain = [('partner_id', '=', coord.partner_id.id),
                          ('address_id', '=', wiz.address_id.id)]
                pc_ids = coord_obj.search(cr, uid, domain, context=context)
                vals = dict(
                    partner_id=coord.partner_id.id,
                    address_id=wiz.address_id.id,
                    vip=coord.vip,
                    unauthorized=coord.unauthorized,
                    coordinate_category_id=coord.coordinate_category_id.id,
                    coordinate_type=coord.coordinate_type,
                    is_main=coord.is_main)
                if not pc_ids:
                    pc_ids = [coord_obj.create(cr, uid, vals, context=context)]
            if pc_ids:
                new_coord_ids.extend(pc_ids)
        if wiz.invalidate:
            postal_coordinate_id =\
                cores.postal_coordinate_ids and\
                cores.postal_coordinate_ids[0].id or False
            if postal_coordinate_id:
                coord_obj.button_undo_allow_duplicate(
                    cr, uid, postal_coordinate_id, context=context)
            co_res_obj.action_invalidate(cr, uid, cores.id, context=context)

        if new_coord_ids:
            ctx = dict(
                context or {}, active_model=coord_obj._name,
                active_ids=new_coord_ids,
                active_id=new_coord_ids[0],
            )
            dupl_wiz_id = dupl_wiz_obj.create(cr, uid, {}, context=ctx)
            res = dupl_wiz_obj.button_allow_duplicate(cr,
                                                      uid,
                                                      [dupl_wiz_id],
                                                      context=ctx)
            if res and res.get('new_co_res') and cores.line or cores.line2:
                new_cor_id = res['res_id']
                vals = dict(line=cores.line,
                            line2=cores.line2)
                co_res_obj.write(cr, uid, new_cor_id, vals, context=context)
            return res
