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
from openerp.addons.ficep_base.selections_translator import translate_selections
from openerp.addons.ficep_retrocession.common import INVOICE_AVAILABLE_TYPES, CALCULATION_METHOD_AVAILABLE_TYPES, CALCULATION_RULE_AVAILABLE_TYPES


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

    _unicity_keys = 'N/A'

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
            self.pool.get('fractionation.line').action_invalidate(cr, uid, [line.id for line in fract_record.fractionation_line_ids], context=context)

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

    _unicity_keys = 'N/A'

# constraints

    _sql_constraints = [
        ('check_unicity_line', 'unique(fractionation_id,power_level_id)', _('This power_level already exists for this fractionation!'))
    ]

    _constraints = [
        (_check_percentage, _('Error ! Percentage should be lower or equal to 100 %'), ['percentage']),
    ]


class calculation_method(orm.Model):
    _name = 'calculation.method'
    _description = 'Calculation method'
    _inherit = ['abstract.ficep.model']

    def _get_method_type(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _get_method_type
        =================
        Get type of calculation method
        :rparam: Type of calculation method
        :rtype: string
        """
        res = {}
        for calculation_method in self.browse(cr, uid, ids, context=context):
            rule_types = list(set([rules.type for rules in calculation_method.calculation_rule_ids]))
            res[calculation_method.id] = rule_types[0] if len(rule_types) == 1 else 'mixed'
        return res

    _type_store_trigger = {
        'calculation.method': (lambda self, cr, uid, ids, context=None: ids, ['calculation_rule_ids'], 20),
        'calculation.rule': (lambda self, cr, uid, ids, context=None:
                               [rule_data['calculation_method_id'][0] for rule_data in self.read(cr, uid, ids, ['calculation_method_id'], context=context) if rule_data['calculation_method_id']],
                               ['type', ], 20)
    }

    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True, track_visibility='onchange'),
        'type': fields.function(_get_method_type, string='Type',
                                 type='selection', store=_type_store_trigger, select=True, selection=CALCULATION_METHOD_AVAILABLE_TYPES),
        'calculation_rule_ids': fields.one2many('calculation.rule', 'calculation_method_id', 'Calculation rules'),
        'mandate_category_ids': fields.one2many('mandate.category', 'calculation_method_id', 'Mandate categories'),
    }

    _unicity_keys = 'N/A'

    def copy_fixed_rules_on_mandate(self, cr, uid, method_id, mandate_id, mandate_key, context=None):
        """
        =================
        copy_fixed_rules_on_mandate
        =================
        copy all fixed linked to method on given mandate
        :rparam: result
        :rtype: Boolean
        Note: Argument vals must be the last in the signature
        """
        rule_pool = self.pool.get('calculation.rule')
        rule_ids = rule_pool.search(cr, uid, [('calculation_method_id', '=', method_id),
                                              ('type', '=', 'fixed')], context=context)
        for rule in rule_pool.browse(cr, uid, rule_ids, context=context):
            data = dict(name=rule.name,
                        type=rule.type,
                        percentage=rule.percentage)
            data[mandate_key] = mandate_id
            rule_pool.create(cr, uid, data, context)

        return True

    def copy_variable_rules_on_retrocession(self, cr, uid, method_id, retrocession_id, context=None):
        """
        =================
        copy_fixed_rules_on_mandate
        =================
        copy all fixed linked to method on given mandate
        :rparam: result
        :rtype: Boolean
        Note: Argument vals must be the last in the signature
        """
        rule_pool = self.pool.get('calculation.rule')
        rule_ids = rule_pool.search(cr, uid, [('calculation_method_id', '=', method_id),
                                              ('type', '=', 'variable')], context=context)
        for rule in rule_pool.browse(cr, uid, rule_ids, context=context):
            data = dict(name=rule.name,
                        type=rule.type,
                        percentage=rule.percentage)
            data['retrocession_id'] = retrocession_id
            rule_pool.create(cr, uid, data, context)

        return True

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
        for method in self.browse(cr, uid, ids, context=context):
            rule_ids = [line.id for line in method.calculation_rule_ids]
        self.pool.get('calculation.rule').action_invalidate(cr, uid, rule_ids, context=context)
        return super(calculation_method, self).action_invalidate(cr, uid, ids, context=context, vals=vals)


class calculation_rule(orm.Model):
    _name = 'calculation.rule'
    _description = 'Calculation rule'
    _inherit = ['abstract.ficep.model']

    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True, track_visibility='onchange'),
        'type': fields.selection(CALCULATION_RULE_AVAILABLE_TYPES, 'Type', required=True),
        'calculation_method_id': fields.many2one('calculation.method', 'Calculation method',
                                        select=True, track_visibility='onchange'),
        'retrocession_id': fields.many2one('retrocession', 'Retrocession',
                                        select=True, track_visibility='onchange'),
        'sta_mandate_id': fields.many2one('sta.mandate', 'State Mandate',
                                        select=True, track_visibility='onchange'),
        'ext_mandate_id': fields.many2one('ext.mandate', 'External Mandate',
                                        select=True, track_visibility='onchange'),
        'percentage': fields.float('Percentage', required=True, track_visibility='onchange'),
        'amount': fields.float('Amount', track_visibility='onchange')
    }

    _unicity_keys = 'N/A'


class retrocession(orm.Model):
    _name = 'retrocession'
    _description = 'Retrocession'
    _inherit = ['abstract.ficep.model']

    def _get_partner_id(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _get_partner_id
        =================
        Get partner_id linked to mandate
        :rparam: Partner id
        :rtype: integer
        """
        res = {}
        for retrocession in self.browse(cr, uid, ids, context=context):
            res[retrocession.id] = retrocession.sta_mandate_id.partner_id if retrocession.sta_mandate_id else retrocession.ext_mandate_id.partner_id
        return res

    def _get_fixed_rule_ids(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _get_fixed_rule_ids
        =================
        Get calculation rule ids linked to mandate
        :rparam: Calculation rule ids
        :rtype: one2many
        """
        res = {}
        for retrocession in self.browse(cr, uid, ids, context=context):
            rules = retrocession.sta_mandate_id.calculation_rule_ids if retrocession.sta_mandate_id else retrocession.ext_mandate_id.calculation_rule_ids
            res[retrocession.id] = [rule.id for rule in rules]
        return res

    def _get_fixed_rule_inactive_ids(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _get_fixed_rule_ids
        =================
        Get calculation rule ids linked to mandate
        :rparam: Calculation rule ids
        :rtype: one2many
        """
        res = {}
        for retrocession in self.browse(cr, uid, ids, context=context):
            res[retrocession.id] = retrocession.sta_mandate_id.calculation_rule_inactive_ids if retrocession.sta_mandate_id else retrocession.ext_mandate_id.calculation_rule_inactive_ids
        return res

    def _compute_amount(self, cr, uid, ids, rule_column, context=None):
        """
        =================
        _compute_amount
        =================
        Get computation of retrocession coming from rules
        :rparam:  retrocession amount
        :rtype: float
        """
        res = {}
        for retrocession in self.browse(cr, uid, ids, context=context):
            if not retrocession.active:
                rule_column.replace('ids', 'inactive_ids')
            amount = 0.0
            for rule in retrocession[rule_column]:
                amount += (rule.amount * (rule.percentage / 100))
            res[retrocession.id] = amount
        return res

    def _compute_fixed_amount(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _compute_fixed_amount
        =================
        Get computation of retrocession coming from fixed rules linked to mandate
        :rparam: Fixed part of retrocession amount
        :rtype: float
        """
        return self._compute_amount(cr, uid, ids, 'fixed_rule_ids', context=context)

    def _compute_variable_amount(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _compute_fixed_amount
        =================
        Get computation of retrocession coming from fixed rules linked to mandate
        :rparam: Fixed part of retrocession amount
        :rtype: float
        """
        return self._compute_amount(cr, uid, ids, 'variable_rule_ids', context=context)

    def _compute_total_amount(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _compute_fixed_amount
        =================
        Get computation of retrocession coming from fixed rules linked to mandate
        :rparam: Fixed part of retrocession amount
        :rtype: float
        """
        res = {}
        fixed_amounts = self._compute_amount(cr, uid, ids, 'fixed_rule_ids', context=context)
        variable_amounts = self._compute_amount(cr, uid, ids, 'variable_rule_ids', context=context)
        for retro_id in ids:
            res[retro_id] = (fixed_amounts[retro_id] + variable_amounts[retro_id])
        return res

    def _get_invoice_type(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _get_invoice_type
        =================
        Get invoice_type linked to mandate
        :rparam: Invoice type
        :rtype: String
        """
        res = {}
        for retrocession in self.browse(cr, uid, ids, context=context):
            res[retrocession.id] = retrocession.sta_mandate_id.invoice_type if retrocession.sta_mandate_id else retrocession.ext_mandate_id.invoice_type
        return res

    _columns = {
        'sta_mandate_id': fields.many2one('sta.mandate', 'State Mandate',
                                        select=True, track_visibility='onchange'),
        'ext_mandate_id': fields.many2one('ext.mandate', 'External Mandate',
                                        select=True, track_visibility='onchange'),
        'partner_id': fields.function(_get_partner_id, string='Representative',
                                 type='many2one', relation='res.partner', store=False, select=True),
        'invoice_type': fields.function(_get_invoice_type, string='Invoicing',
                                 type='selection', selection=INVOICE_AVAILABLE_TYPES, store=False, select=True),
        'month': fields.selection(fields.date.MONTHS, 'Month', size=128, select=True, track_visibility='onchange'),
        'year': fields.char('Year', size=128, select=True, track_visibility='onchange'),
        'variable_rule_ids': fields.one2many('calculation.rule', 'retrocession_id', 'Calculation variable rules', domain=[('active', '=', True)]),
        'variable_rule_inactive_ids': fields.one2many('calculation.rule', 'retrocession_id', 'Calculation variable rules', domain=[('active', '=', False)]),
        'fixed_rule_ids': fields.function(_get_fixed_rule_ids, string='Calculation fixed rules',
                                 type='one2many', relation='calculation.rule', store=False, select=True),
        'fixed_rule_inactive_ids': fields.function(_get_fixed_rule_inactive_ids, string='Calculation fixed rules',
                                 type='one2many', relation='calculation.rule', store=False, select=True),
        'fixed_amount': fields.function(_compute_fixed_amount, string='Fixed amount to retrocede',
                                 type='float', store=False, select=True),
        'variable_amount': fields.function(_compute_variable_amount, string='Variable amount to retrocede',
                                 type='float', store=False, select=True),
        'total_amount': fields.function(_compute_total_amount, string='Total amount to retrocede',
                                 type='float', store=False, select=True),
    }

    def _check_unicity(self, cr, uid, ids, for_unlink=False, context=None):
        """
        =================
        _check_unicity
        =================
        Check if partner doesn't have several retrocession at the same period
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        retrocessions = self.browse(cr, uid, ids)
        for retro in retrocessions:
            if retro.sta_mandate_id:
                key = 'sta_mandate_id'
            else:
                key = 'ext_mandate_id'
            if len(self.search(cr, uid, [(key, '=', retro[key].id), ('id', '!=', retro.id), ('month', '=', retro.month), ('year', '=', retro.year)], context=context)) > 0:
                return False

        return True

    _constraints = [
        (_check_unicity, _("A retrocession already exists for this mandate at this period"), ['sta_mandate_id', 'ext_mandate_id'])
    ]

    _unicity_keys = 'N/A'

    #orm methods
    def create(self, cr, uid, vals, context=None):
        res = super(retrocession, self).create(cr, uid, vals, context=context)
        if res:
            retro = self.browse(cr, uid, res, context=context)
            mandate_rec = None
            if retro.sta_mandate_id:
                mandate_rec = retro.sta_mandate_id
            elif retro.ext_mandate_id:
                mandate_rec = retro.ext_mandate_id

            if mandate_rec.calculation_method_id:
                self.pool.get('calculation.method').copy_variable_rules_on_retrocession(cr, uid, mandate_rec.calculation_method_id.id, retro.id, context=context)

        return res

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []
        for retro in self.browse(cr, uid, ids, context=context, fields_process=translate_selections):
            mandate_id = False
            mandate_model = False
            if retro.sta_mandate_id:
                mandate_model = 'sta.mandate'
                mandate_id = retro.sta_mandate_id.id
            elif retro.ext_mandate_id:
                mandate_model = 'ext.mandate'
                mandate_id = retro.ext_mandate_id.id
            mandate_name = self.pool.get(mandate_model).name_get(cr, uid, mandate_id, context=context)

            if retro.month:
                display_name = u'{mandate} ({month} {year})'.format(month=retro.month,
                                                                    year=retro.year,
                                                                    mandate=mandate_name[0][1])
            else:
                display_name = u'{mandate} ({year})'.format(year=retro.year,
                                                            mandate=mandate_name[0][1])

            res.append((retro['id'], display_name))
        return res

# view methods: onchange, button
    def onchange_sta_mandate_id(self, cr, uid, ids, sta_mandate_id, context=None):
        res = {}
        if sta_mandate_id:
            invoice_type = self.pool.get('sta.mandate').read(cr, uid, sta_mandate_id, ['invoice_type'], context)['invoice_type']
            res['value'] = dict(invoice_type=invoice_type or False)

        return res

    def onchange_ext_mandate_id(self, cr, uid, ids, ext_mandate_id, context=None):
        res = {}
        if ext_mandate_id:
            invoice_type = self.pool.get('ext.mandate').read(cr, uid, ext_mandate_id, ['invoice_type'], context)['invoice_type']
            res['value'] = dict(invoice_type=invoice_type or False)

        return res

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
        for retro in self.browse(cr, uid, ids, context=context):
            self.pool.get('calculation.rule').action_invalidate(cr, uid, [rule.id for rule in retro.variable_rule_ids], context=context)

        return super(fractionation, self).action_invalidate(cr, uid, ids, context=context, vals=vals)
