# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields


class int_instance(fields.function):
    '''
    Implement a function field that does not recall the compute method when useless
    in this case the get method of a simple m2o field is called
    '''

    def __init__(self, fnct, **args):
        super(int_instance, self).__init__(fnct, **args)
        self._auto_join = False

    def get(self, cr, obj, ids, name, uid=False, context=None, values=None):
        context = context or {}
        if context.get('just_4_reading'):
            # currently it is a copy/paste from fields.many2one.get
            if values is None:
                values = {}

            res = {}
            for r in values:
                res[r['id']] = r[name]
            for id in ids:
                res.setdefault(id, '')
            obj = obj.pool[self._obj]

            records = dict(obj.name_get(cr, SUPERUSER_ID,
                                        list(set([x for x in res.values() if isinstance(x, (int, long))])),
                                        context=context))
            for id in res:
                if res[id] in records:
                    res[id] = (res[id], records[res[id]])
                else:
                    res[id] = False
        else:
            res = super(int_instance, self).get(cr, obj, ids, name, uid=uid, context=context, values=values)
        return res


class res_partner(orm.Model):

    _inherit = "res.partner"

    def _get_instance_id(self, cr, uid, ids, name, args, context=None):
        """
        ================
        _get_instance_id
        ================
        Replicate reference int_instance_id on partner
        :param ids: partner ids for which int_instance_id have to be recomputed
        :type name: char
        :rparam: dictionary for all partner id with int_instance_id
        :rtype: dict {partner_id: int_instance_id, ...}
        Note:
        Calling and result convention: Single mode
        """
        result = {}.fromkeys(ids, False)

        def_int_instance_id = self.pool.get('int.instance').get_default(cr, uid)
        for partner in self.browse(cr, uid, ids, context=context):
            result[partner.id] = partner.int_instance_id.id or def_int_instance_id

        coord_obj = self.pool['postal.coordinate']
        coordinate_ids = coord_obj.search(cr, SUPERUSER_ID, [('partner_id', 'in', ids),
                                                             ('is_main', '=', True),
                                                             ('active', '<=', True)], context=context)
        for coord in coord_obj.browse(cr, uid, coordinate_ids, context=context):
            if coord.active == coord.partner_id.active:
                if coord.address_id.address_local_zip_id:
                    result[coord.partner_id.id] = coord.address_id.address_local_zip_id.int_instance_id.id
        return result

    def _accept_anyway(self, cr, uid, ids, name, value, args, context=None):
        '''
        Accept the modification of the internal instance
        Do not make a self.write here, it will indefinitively loop on itself...
        '''
        cr.execute('update %s set %s = %%s where id = %s' % (self._table, name, ids), (value or None, ))
        return True

    _instance_store_triggers = {
        'postal.coordinate': (lambda self, cr, uid, ids, context=None: self.pool['postal.coordinate'].get_linked_partners(cr, uid, ids, context=context),
            ['partner_id', 'address_id', 'is_main', 'active'], 10),
        'address.address': (lambda self, cr, uid, ids, context=None: self.pool['address.address'].get_linked_partners(cr, uid, ids, context=context),
            ['address_local_zip_id'], 10),
        'address.local.zip': (lambda self, cr, uid, ids, context=None: self.pool['address.local.zip'].get_linked_partners(cr, uid, ids, context=context),
            ['int_instance_id'], 10),
    }

    _columns = {
        'int_instance_id': int_instance(_get_instance_id, string='Internal Instance',
                                        type='many2one', relation='int.instance', select=True,
                                        store=_instance_store_triggers, fnct_inv=_accept_anyway),

        'int_instance_m2m_ids': fields.many2many('int.instance', 'res_partner_int_instance_rel', id1='partner_id', id2='int_instance_id', string='Internal Instances'),
    }

    _defaults = {
        'int_instance_id': lambda self, cr, uid, ids, context=None: self.pool.get('int.instance').get_default(cr, uid),
    }

# orm methods

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy m2m fields.
        """
        default = default or {}
        default.update({
            'int_instance_m2m_ids': [],
        })
        res = super(res_partner, self).copy_data(cr, uid, ids, default=default, context=context)
        return res

    def _read_flat(self, cr, uid, ids, fields_to_read, context=None, load='_classic_read'):
        """
        Escape the recomputing of field value if not useful
        """
        context = context or {}
        context.update({
            'just_4_reading': True,
        })
        res = super(res_partner, self)._read_flat(cr, uid, ids, fields_to_read, context=context, load=load)
        context.update({
            'just_4_reading': False,
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
