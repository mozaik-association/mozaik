# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_retrocession, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_retrocession is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_retrocession is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_retrocession.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm, fields


class sta_assembly(orm.Model):

    _name = 'sta.assembly'
    _inherit = ['sta.assembly']
    _description = 'State Assembly'

    def get_linked_sta_mandate_ids(self, cr, uid, ids, context=None):
        """
        ==============================
        get_linked_sta_mandate_ids
        ==============================
        Return State Mandate ids linked to assembly
        :rparam: sta_mandate_ids
        :rtype: list of ids
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        return self.pool.get('sta.mandate').search(
            cr, uid, [
                ('sta_assembly_id', 'in', ids)], context=context)

    _columns = {
        'fractionation_id': fields.many2one(
            'fractionation',
            'Fractionation',
            select=True,
            track_visibility='onchange'),
        'calculation_method_id': fields.many2one(
            'calculation.method',
            string='Calculation Method',
            select=True,
            track_visibility='onchange'),
        'retro_instance_id': fields.many2one(
            'int.instance',
            'Retrocessions Management Instance',
            select=True,
            track_visibility='onchange'),
    }


class ext_assembly(orm.Model):

    _name = 'ext.assembly'
    _inherit = ['ext.assembly']
    _description = 'External Assembly'

    def get_linked_ext_mandate_ids(self, cr, uid, ids, context=None):
        """
        ==============================
        get_linked_ext_mandate_ids
        ==============================
        Return External Mandate ids linked to assembly
        :rparam: sta_mandate_ids
        :rtype: list of ids
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        return self.pool.get('ext.mandate').search(
            cr, uid, [
                ('ext_assembly_id', 'in', ids)], context=context)

    _columns = {
        'fractionation_id': fields.many2one(
            'fractionation',
            'Fractionation',
            select=True,
            track_visibility='onchange'),
        'calculation_method_id': fields.many2one(
            'calculation.method',
            string='Calculation Method',
            select=True,
            track_visibility='onchange'),
        'retro_instance_id': fields.many2one(
            'int.instance',
            'Retrocessions Management Instance',
            select=True,
            track_visibility='onchange'),
    }
