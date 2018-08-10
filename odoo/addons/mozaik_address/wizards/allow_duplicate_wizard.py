# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields


class allow_duplicate_wizard(orm.TransientModel):

    _inherit = "allow.duplicate.wizard"
    _name = "allow.duplicate.address.wizard"

    _columns = {
        'address_id': fields.many2one(
            'address.address', string='Co-Residency',
            readonly=True, ondelete='cascade'),
        'co_residency_id': fields.many2one(
            'co.residency', string='Co-Residency',
            readonly=True, ondelete='cascade'),
    }

    def default_get(self, cr, uid, fields, context):
        """
        To get default values for the object.
        """
        res = super(allow_duplicate_wizard, self).default_get(
            cr, uid, fields, context=context)
        context = context or {}

        ids = context.get('active_id') and \
            [context.get('active_id')] or \
            context.get('active_ids') or []
        for coord_id in ids:
            vals = self.pool['postal.coordinate'].read(
                cr, uid, coord_id, ['address_id'], context=context)
            address_id = vals['address_id'][0]
            res['address_id'] = address_id
            cor_ids = self.pool['co.residency'].search(
                cr, uid, [('address_id', '=', address_id)], context=context)
            if cor_ids:
                res['co_residency_id'] = cor_ids[0]
            break

        return res

    def button_allow_duplicate(self, cr, uid, ids, context=None, vals=None):
        """
        Create co_residency if any.
        """
        context = context or {}

        wizard = self.browse(cr, uid, ids, context=context)[0]
        new_co = False
        if wizard.co_residency_id:
            cor_id = wizard.co_residency_id.id
        else:
            vals = {'address_id': wizard.address_id.id}
            cor_id = self.pool['co.residency'].create(
                cr, uid, vals, context=context)
            new_co = True

        vals = {'co_residency_id': cor_id}
        super(allow_duplicate_wizard, self).button_allow_duplicate(
            cr, uid, ids, context=context, vals=vals)

        if context and context.get('get_co_residency', False):
            return cor_id

        # go directly to the newly created co-residency
        res = self.pool['co.residency'].display_object_in_form_view(
            cr, uid, cor_id, context=context)
        if res and new_co:
            res['new_co_res'] = True
        return res
