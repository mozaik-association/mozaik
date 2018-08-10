# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools.translate import _


class co_residency(orm.Model):

    _name = 'co.residency'
    _inherit = ['mozaik.abstract.model']
    _description = 'Co-Residency'

    _inactive_cascade = True

    _columns = {
        'address_id': fields.many2one(
            'address.address', string='Address',
            required=True, readonly=True, select=True),
        'line': fields.char('Line 1', track_visibility='onchange'),
        'line2': fields.char('Line 2', track_visibility='onchange'),

        'postal_coordinate_ids': fields.one2many(
            'postal.coordinate', 'co_residency_id',
            string='Postal Coordinates'),
    }

    _rec_name = 'address_id'

    _unicity_keys = 'address_id'

    def name_get(self, cr, uid, ids, context=None):
        """
        :rparam: list of (id, name)
                 where id is the id of each object
                 and name, the name to display.
        :rtype: [(id, name)] list of tuple
        """
        if not ids:
            return []

        context = context or self.pool['res.users'].context_get(cr, uid)

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []
        for record in self.read(cr, uid, ids, ['line', 'line2'],
                                context=context):
            if not record['line'] and not record['line2']:
                name = _("Co-Residency to complete")
            else:
                name = "/".join([line for line in
                                 [record['line'], record['line2']] if line])
            res.append((record['id'], name))
        return res

    def unlink(self, cr, uid, ids, context=None):
        '''
        Force "undo allow duplicate" when deleting a co-residency
        '''
        ids = isinstance(ids, (long, int)) and [ids] or ids
        coords = self.read(
            cr, uid, ids, ['postal_coordinate_ids'], context=context)
        cids = []
        for c in coords:
            cids += c['postal_coordinate_ids']
        if cids:
            self.pool['postal.coordinate'].button_undo_allow_duplicate(
                cr, uid, cids, context=context)
        res = super(co_residency, self).unlink(cr, uid, ids, context=context)
        return res
