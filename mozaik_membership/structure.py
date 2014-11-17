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


# these 2 classes should be merged into one inherited abstract class of
# abstract.assembly
# unfortunately that does not work: methods is never called !!
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
        return res

    def write(self, cr, uid, ids, vals, context=None):
        '''
        Update the Responsible Internal Instance linked to the result Partner
        '''
        if 'instance_id' in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super(int_assembly, self).\
            write(cr, uid, ids, vals, context=context)
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
