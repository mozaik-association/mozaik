# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import fields, api
from openerp.osv import orm


class sta_assembly(orm.Model):

    _inherit = 'sta.assembly'

# static methods

    def _pre_update(self, cr, uid, vals, context=None):
        '''
        When instance_id is touched force an update of int_instance_id
        '''
        res = {}
        if 'instance_id' in vals:
            instance_id = vals['instance_id']
            int_instance_id = self.pool['sta.instance'].\
                read(cr, uid, instance_id, ['int_instance_id'],
                     context=context)['int_instance_id']
            if int_instance_id:
                res = {'int_instance_id': int_instance_id[0]}
        return res

# orm methods

    def create(self, cr, uid, vals, context=None):
        '''
        Set the Responsible Internal Instance linked to the result Partner
        '''
        if 'instance_id' in vals:
            vals.update(self._pre_update(cr, uid, vals, context=context))
        res = super(sta_assembly, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        '''
        Update the Responsible Internal Instance linked to the result Partner
        '''
        vals.update(self._pre_update(cr, uid, vals, context=context))
        res = super(sta_assembly, self).write(
            cr, uid, ids, vals, context=context)
        return res


class int_instance(orm.Model):

    _inherit = 'int.instance'

    def _compute_member_count(self):
        partner_obj = self.env['res.partner']
        for int_instance in self:
            domain = [
                ('int_instance_id', '=', int_instance.id),
                ('is_company', '=', False)
            ]
            int_instance.member_count = partner_obj.search_count(domain)

    member_count = fields.Integer(
        compute=_compute_member_count, type='integer', string='Members')

# orm methods

    def create(self, cr, uid, vals, context=None):
        res = super(int_instance, self).create(cr, uid, vals, context=context)
        self.pool['ir.rule'].clear_cache(cr, uid)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(int_instance, self).write(
            cr, uid, ids, vals, context=context)
        if 'partner_id' in vals:
            self.pool['ir.rule'].clear_cache(cr, uid)
        return res

    def unlink(self, cr, uid, ids, context=None):
        res = super(int_instance, self).unlink(cr, uid, ids, context=context)
        self.pool['ir.rule'].clear_cache(cr, uid)
        return res

# public methods

    def get_default(self, cr, uid, context=None):
        """
        Returns the default Internal Instance
        """
        res = [super(int_instance, self).get_default(cr, uid, context=context)]
        if res:
            res = self.search(cr, uid, [('id', 'in', res)], context=context)
        if not res:
            res = self.pool['res.users'].internal_instances(cr, uid)
        return res and res[0] or False


class int_assembly(orm.Model):

    _inherit = 'int.assembly'

# orm methods

    def create(self, cr, uid, vals, context=None):
        '''
        Responsible Internal Instance linked to the result Partner is the
        Instance of the Assembly
        '''
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super(int_assembly, self).create(cr, uid, vals, context=context)
        self.pool['ir.rule'].clear_cache(cr, uid)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        '''
        Update the Responsible Internal Instance linked to the result Partner
        '''
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super(int_assembly, self).write(
            cr, uid, ids, vals, context=context)
        self.pool['ir.rule'].clear_cache(cr, uid)
        return res

    def unlink(self, cr, uid, ids, context=None):
        res = super(int_assembly, self).unlink(cr, uid, ids, context=context)
        self.pool['ir.rule'].clear_cache(cr, uid)
        return res


class ext_assembly(orm.Model):

    _inherit = 'ext.assembly'

# orm methods

    def create(self, cr, uid, vals, context=None):
        '''
        Responsible Internal Instance linked to the result Partner is
        the Instance of the Assembly
        '''
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super(ext_assembly, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        '''
        Update the Responsible Internal Instance linked to the result Partner
        '''
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super(ext_assembly, self).write(cr, uid, ids, vals,
                                              context=context)
        return res
