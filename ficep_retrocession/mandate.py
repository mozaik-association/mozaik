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
from structure import sta_assembly, ext_assembly
from openerp.addons.ficep_retrocession.common import INVOICE_AVAILABLE_TYPES, CALCULATION_METHOD_AVAILABLE_TYPES


class mandate_category(orm.Model):

    _name = 'mandate.category'
    _description = 'Mandate Category'
    _inherit = ['mandate.category']

    def get_linked_sta_mandate_ids(self, cr, uid, ids, context=None):
        return super(mandate_category, self).get_linked_sta_mandate_ids(cr, uid, ids, context=context)

    def get_linked_ext_mandate_ids(self, cr, uid, ids, context=None):
        return super(mandate_category, self).get_linked_ext_mandate_ids(cr, uid, ids, context=context)

    _columns = {
        'fractionation_id': fields.many2one('fractionation', string='Fractionation', track_visibility='onchange'),
        'calculation_method_id': fields.many2one('calculation.method', string='Calculation method', track_visibility='onchange'),
        'invoice_type': fields.selection(INVOICE_AVAILABLE_TYPES, 'Invoicing', required=True)
    }

    _defaults = {
        'invoice_type': INVOICE_AVAILABLE_TYPES[2][0]
    }


class sta_mandate(orm.Model):
    _name = 'sta.mandate'
    _description = 'State Mandate'
    _inherit = ['sta.mandate']

    def _get_method_id(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _get_method_id
        =================
        Get id of calculation method
        :rparam: id of calculation method
        :rtype: integer
        """
        res = {}
        for sta_mandate in self.browse(cr, uid, ids, context=context):
            cat_method = sta_mandate.mandate_category_id.calculation_method_id
            ass_method = sta_mandate.sta_assembly_id.calculation_method_id

            if ass_method:
                method_id = ass_method.id
            elif cat_method:
                method_id = cat_method.id
            else:
                method_id = False
            res[sta_mandate.id] = method_id
        return res

    _method_id_store_trigger = {
        'sta.mandate': (lambda self, cr, uid, ids, context=None: ids,
            ['sta_assembly_id', 'mandate_category_id'], 20),
        'mandate.category': (mandate_category.get_linked_sta_mandate_ids, ['calculation_method_id'], 20),
        'sta.assembly': (sta_assembly.get_linked_sta_mandate_ids, ['calculation_method_id'], 20),
    }

    _columns = {
        'invoice_type': fields.related('mandate_category_id', 'invoice_type', string='Invoicing', type='selection',
                                       selection=INVOICE_AVAILABLE_TYPES, store=True),
        'calculation_method_id': fields.function(_get_method_id, string='Calculation Method',
                                 type='many2one', relation="calculation.method", store=_method_id_store_trigger, select=True),
        'method_type': fields.related('calculation_method_id', 'type', string='Calculation method type', type='selection',
                                       selection=CALCULATION_METHOD_AVAILABLE_TYPES, store=_method_id_store_trigger),
        'calculation_rule_ids': fields.one2many('calculation.rule', 'sta_mandate_id', 'Calculation rules', domain=[('active', '=', True)]),
        'calculation_rule_inactive_ids': fields.one2many('calculation.rule', 'sta_mandate_id', 'Calculation rules', domain=[('active', '=', False)]),
    }

    #orm methods
    def create(self, cr, uid, vals, context=None):
        res = super(sta_mandate, self).create(cr, uid, vals, context=context)
        if res:
            mandate = self.browse(cr, uid, res, context=context)
            if mandate.calculation_method_id:
                self.pool.get('calculation.method').copy_fixed_rules_on_mandate(cr, uid, mandate.calculation_method_id.id, mandate.id, 'sta_mandate_id', context=context)

        return res


class ext_mandate(orm.Model):
    _name = 'ext.mandate'
    _description = 'External Mandate'
    _inherit = ['ext.mandate']

    def _get_method_id(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _get_method_id
        =================
        Get id of calculation method
        :rparam: id of calculation method
        :rtype: integer
        """
        res = {}
        for ext_mandate in self.browse(cr, uid, ids, context=context):
            cat_method = ext_mandate.mandate_category_id.calculation_method_id
            ass_method = ext_mandate.ext_assembly_id.calculation_method_id

            if ass_method:
                method_id = ass_method.id
            elif cat_method:
                method_id = cat_method.id
            else:
                method_id = False
            res[ext_mandate.id] = method_id
        return res

    _method_id_store_trigger = {
        'ext.mandate': (lambda self, cr, uid, ids, context=None: ids,
            ['ext_assembly_id', 'mandate_category_id'], 20),
        'mandate.category': (mandate_category.get_linked_ext_mandate_ids, ['calculation_method_id'], 20),
        'ext.assembly': (ext_assembly.get_linked_ext_mandate_ids, ['calculation_method_id'], 20),
    }

    _columns = {
        'invoice_type': fields.related('mandate_category_id', 'invoice_type', string='Invoicing', type='selection',
                                       selection=INVOICE_AVAILABLE_TYPES, store=True),
        'calculation_method_id': fields.function(_get_method_id, string='Calculation Method',
                                 type='many2one', relation="calculation.method", store=_method_id_store_trigger, select=True),
        'method_type': fields.related('calculation_method_id', 'type', string='Calculation method type', type='selection',
                                       selection=CALCULATION_METHOD_AVAILABLE_TYPES, store=_method_id_store_trigger),
        'calculation_rule_ids': fields.one2many('calculation.rule', 'sta_mandate_id', 'Calculation rules', domain=[('active', '=', True)]),
        'calculation_rule_inactive_ids': fields.one2many('calculation.rule', 'sta_mandate_id', 'Calculation rules', domain=[('active', '=', False)]),
    }

    #orm methods
    def create(self, cr, uid, vals, context=None):
        res = super(ext_mandate, self).create(cr, uid, vals, context=context)
        if res:
            mandate = self.browse(cr, uid, res, context=context)
            if mandate.calculation_method_id:
                self.pool.get('calculation.method').copy_fixed_rules_on_mandate(cr, uid, mandate.calculation_method_id.id, mandate.id, 'ext_mandate_id', context=context)

        return res
