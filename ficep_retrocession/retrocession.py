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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class fractionation(orm.Model):
    _name = 'fractionation'
    _description = 'Fractionation'
    _inherit = ['abstract.ficep.model']

    _total_percentage_store_trigger = {
        'fractionation.line': (lambda self, cr, uid, ids, context=None:
                               [line_data['fractionation_id'][0] for line_data in self.read(cr, uid, ids, ['fractionation_id'], context=context)],
                               ['percentage', ], 20)
    }

    def _compute_total_percentage(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _compute_total_percentage
        =================
        Compute total of percentage of each lines
        :rparam: total of percentage of each lines
        :rtype: float
        """
        res = {}
        for fractionation in self.browse(cr, uid, ids, context=context):
            res[fractionation.id] = sum([line.percentage for line in fractionation.fractionation_line_ids])
        return res

    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True, track_visibility='onchange'),
        'mandate_category_ids': fields.one2many('mandate.category', 'fractionation_id', 'Mandate categories'),
        'fractionation_line_ids': fields.one2many('fractionation.line', 'fractionation_id', 'Fractionation Lines', domain=[('active', '=', True)]),
        'fractionation_line_inactive_ids': fields.one2many('fractionation.line', 'fractionation_id', 'Fractionation Lines', domain=[('active', '=', False)]),
        'total_percentage': fields.function(_compute_total_percentage, string='Total Percentage',
                                 type='float', store=_total_percentage_store_trigger, select=True),
    }

    def action_invalidate(self, cr, uid, ids, context=None, vals=None):
        """
        =================
        action_invalidate
        =================
        Invalidates an object
        :rparam: True
        :rtype: boolean
        Note: Argument vals must be the last in the signature
        """
        for fract_record in self.browse(cr, uid, ids, context=context):
            line_ids = [line.id for line in fract_record.fractionation_line_ids]
        self.pool.get('fractionation.line').action_invalidate(cr, uid, line_ids, context=context)
        return super(fractionation, self).action_invalidate(cr, uid, ids, context=context, vals=vals)


class fractionation_line(orm.Model):
    _name = 'fractionation.line'
    _description = 'Fractionation Line'
    _inherit = ['abstract.ficep.model']

    def _check_percentage(self, cr, uid, ids, context=None):
        """
        =================
        _check_percentage
        =================
        Check if percentage is lower or equal to 100 %
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        for line_data in self.read(cr, uid, ids, ['percentage'], context=context):
            if line_data['percentage'] > 100.00:
                return False
        return True

    _columns = {
        'fractionation_id': fields.many2one('fractionation', 'Fractionation',
                                                select=True, required=True, track_visibility='onchange'),
        'power_level_id': fields.many2one('int.power.level', 'Internal Power Level', required=True, track_visibility='onchange'),
        'percentage': fields.float('Percentage', required=True, track_visibility='onchange')
    }

# constraints

    _sql_constraints = [
        ('check_unicity_line', 'unique(fractionation_id,power_level_id)', _('This power_level already exists for this fractionation!'))
    ]

    _constraints = [
        (_check_percentage, _('Error ! Percentage should be lower or equal to 100 %'), ['percentage']),
    ]
