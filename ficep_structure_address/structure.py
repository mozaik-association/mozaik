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


class abstract_assembly(orm.AbstractModel):

    _name = 'abstract.assembly'
    _inherit = ['abstract.assembly']

# orm methods

    def create(self, cr, uid, vals, context=None):
        '''
        Responsible Internal Instance is the Instance
        Note: must be override for State Instance
        '''
        if 'int_instance_id' not in vals:
            vals.update({'int_instance_id': vals['instance_id']})
        res = super(abstract_assembly, self).create(cr, uid, vals, context=context)
        return res


class sta_assembly(orm.Model):

    _inherit = 'sta.assembly'

# orm methods

    def create(self, cr, uid, vals, context=None):
        '''
        Responsible Internal Instance is the Internal
        Instance attached to the State Instance
        '''
        instance_id = vals['instance_id']
        int_instance_id = self.pool['sta.instance'].read(cr, uid, instance_id, ['int_instance_id'], context=context)['int_instance_id'][0]
        vals.update({'int_instance_id': int_instance_id})
        res = super(sta_assembly, self).create(cr, uid, vals, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
