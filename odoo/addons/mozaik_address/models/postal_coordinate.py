# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools.translate import _


class postal_coordinate(orm.Model):

    _name = 'postal.coordinate'
    _inherit = ['abstract.coordinate']
    _description = 'Postal Coordinate'

    _track = {
        'bounce_counter': {
            'mozaik_address.address_failure_notification':
                lambda self, cr, uid, obj, ctx=None: obj.bounce_counter,
        },
    }

    _discriminant_field = 'address_id'
    _trigger_fields = []
    _undo_redirect_action = 'mozaik_address.postal_coordinate_action'

    _columns = {
        'address_id':
            fields.many2one(
                'address.address', string='Address', required=True,
                readonly=True, select=True),
        'co_residency_id':
            fields.many2one('co.residency', string='Co-Residency', select=True)
    }

    _rec_name = _discriminant_field

    _unicity_keys = 'partner_id, %s' % _discriminant_field

    def onchange_unauthorized(
            self, cr, uid, ids, unauthorized, co_residency_id, context=None):
        if unauthorized and co_residency_id:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _(
                        'Unauthorizing a coordinate usually involves '
                        'a change in its co-residency.'
                    )
                }
            }

    def name_get(self, cr, uid, ids, context=None):
        result = super(postal_coordinate, self).name_get(
            cr, uid, ids, context=context)
        new_result = []
        for res in result:
            data = self.read(cr, uid, res[0], ['co_residency_id'],
                             context=context)
            name = res[1]
            if data['co_residency_id']:
                name = "%s (%s)" % (name, data['co_residency_id'][1])
            new_result.append((res[0], name))
        return new_result

    def get_fields_to_update(self, cr, uid, mode, context=None):
        """
        :type mode: char
        :param mode: mode defining return values
        :rtype: dictionary
        :rparam: values to update
        """
        res = super(postal_coordinate, self).get_fields_to_update(
            cr, uid, mode, context=context)
        if mode in ['duplicate', 'reset']:
            res.update({'co_residency_id': False})
        return res
