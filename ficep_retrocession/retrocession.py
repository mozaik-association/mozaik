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

from datetime import datetime

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.ficep_base.selections_translator import translate_selections
import openerp.addons.decimal_precision as dp

from .common import RETROCESSION_MODES_AVAILABLE, CALCULATION_METHOD_AVAILABLE_TYPES, CALCULATION_RULE_AVAILABLE_TYPES

RETROCESSION_AVAILABLE_STATES = [
    ('draft', 'Open'),
    ('validated', 'Validated'),
    ('paid', 'Done'),
    ('cancelled', 'Cancelled'),
]


class fractionation(orm.Model):
    _name = 'fractionation'
    _description = 'Fractionation'
    _inherit = ['abstract.ficep.model']

    _inactive_cascade = True

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
            lines = fractionation.active and fractionation.fractionation_line_ids or fractionation.fractionation_line_inactive_ids
            res[fractionation.id] = sum([line.percentage for line in lines])
        return res

    _total_percentage_store_trigger = {
        'fractionation': (lambda self, cr, uid, ids, context=None: ids, ['fractionation_line_ids', 'active'], 20),
        'fractionation.line': (lambda self, cr, uid, ids, context=None:
                               [line_data['fractionation_id'][0] for line_data in self.read(cr, uid, ids, ['fractionation_id'], context=context)],
                               ['percentage', 'active', ], 20),
    }

    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True, track_visibility='onchange'),
        'mandate_category_ids': fields.one2many('mandate.category', 'fractionation_id', 'Mandate categories'),
        'fractionation_line_ids': fields.one2many('fractionation.line', 'fractionation_id', 'Fractionation Lines', domain=[('active', '=', True)]),
        'fractionation_line_inactive_ids': fields.one2many('fractionation.line', 'fractionation_id', 'Fractionation Lines', domain=[('active', '=', False)]),
        'total_percentage': fields.function(_compute_total_percentage, string='Total Percentage',
                                 type='float', store=_total_percentage_store_trigger, digits_compute=dp.get_precision('Percentage')),
    }

    _order = 'name'

# constraints

    _unicity_keys = 'name'

# orm methods

    def copy_data(self, cr, uid, id_, default=None, context=None):
        res = super(fractionation, self).copy_data(cr, uid, id_, default=default, context=context)

        res.update({
            'name': _('%s (copy)') % res.get('name'),
        })
        return res


class fractionation_line(orm.Model):
    _name = 'fractionation.line'
    _description = 'Fractionation Line'
    _inherit = ['abstract.ficep.model']

    _columns = {
        'fractionation_id': fields.many2one('fractionation', 'Fractionation', required=True, select=True, track_visibility='onchange'),
        'power_level_id': fields.many2one('int.power.level', 'Internal Power Level', required=True, select=True, track_visibility='onchange'),
        'percentage': fields.float('Percentage', required=True, track_visibility='onchange', digits_compute=dp.get_precision('Percentage'))
    }

    _order = 'fractionation_id, power_level_id'

    _rec_name = 'power_level_id'

# constraints

    _unicity_keys = 'fractionation_id, power_level_id'

    _sql_constraints = [
        ('lessthan100_line', 'check(0.0 < percentage and percentage <= 100.0)', 'Percentage should be greater than zero and lower or equal to 100 %')
    ]


class calculation_method(orm.Model):
    _name = 'calculation.method'
    _description = 'Calculation Method'
    _inherit = ['abstract.ficep.model']

    _inactive_cascade = True

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
                               [rule_data['calculation_method_id'][0] for rule_data in self.pool['calculation.rule'].read(cr, uid, ids, ['calculation_method_id'], context=context) if rule_data['calculation_method_id']],
                               ['type', ], 20),
    }

    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True, track_visibility='onchange'),
        'type': fields.function(_get_method_type, string='Type',
                                 type='selection', store=_type_store_trigger, select=True, selection=CALCULATION_METHOD_AVAILABLE_TYPES),
        'calculation_rule_ids': fields.one2many('calculation.rule', 'calculation_method_id', 'Calculation Rules'),
        'mandate_category_ids': fields.one2many('mandate.category', 'calculation_method_id', 'Mandate Categories'),
    }

    _order = 'name'

# constraints

    _unicity_keys = 'name'

# public methods

    def copy_fixed_rules_on_mandate(self, cr, uid, method_id, mandate_id, mandate_key, context=None):
        """
        ===========================
        copy_fixed_rules_on_mandate
        ===========================
        copy all fixed linked to method on given mandate
        :rparam: result
        :rtype: Boolean
        """
        rule_pool = self.pool.get('calculation.rule')
        rule_ids = rule_pool.search(cr, uid, [(mandate_key, '=', mandate_id),
                                              ('type', '=', 'fixed')], context=context)
        if rule_ids:
            rule_pool.unlink(cr, uid, rule_ids, context=context)

        if method_id:
            rule_ids = rule_pool.search(cr, uid, [('calculation_method_id', '=', method_id),
                                                  ('type', '=', 'fixed')], context=context)
            for rule in rule_pool.browse(cr, uid, rule_ids, context=context):
                data = rule_pool.get_copy_fields_value(cr, uid, rule)
                data[mandate_key] = mandate_id
                rule_pool.create(cr, uid, data, context=context)

        return True

    def copy_variable_rules_on_retrocession(self, cr, uid, method_id, retrocession_id, context=None):
        """
        ===================================
        copy_variable_rules_on_retrocession
        ===================================
        copy all variable rules linked to method on given retrocession
        :rparam: result
        :rtype: Boolean
        """
        rule_pool = self.pool.get('calculation.rule')
        if method_id:
            rule_ids = rule_pool.search(cr, uid, [('calculation_method_id', '=', method_id),
                                                  ('type', '=', 'variable')], context=context)
            for rule in rule_pool.browse(cr, uid, rule_ids, context=context):
                data = rule_pool.get_copy_fields_value(cr, uid, rule)
                data['retrocession_id'] = retrocession_id
                rule_pool.create(cr, uid, data, context=context)

        return True


class calculation_rule(orm.Model):
    _name = 'calculation.rule'
    _description = 'Calculation Rule'
    _inherit = ['abstract.ficep.model']

    def _compute_subtotal(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _compute_subtotal
        =================
        compute subtotal of rule
        :rparam: subtotal
        :rtype: float
        """
        res = {}
        for rule in self.browse(cr, uid, ids, context=context):
            coef = -1 if rule.is_deductible else 1
            res[rule.id] = (rule.amount * (rule.percentage / 100)) * coef
        return res

    def _check_percentage(self, cr, uid, ids, for_unlink=False, context=None):
        """
        =================
        _check_percentage
        =================
        Check if percentage is positive for deductible rule
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        for rule in self.browse(cr, uid, ids, context=context):
            return False if (rule.is_deductible and rule.percentage < 0) else True

    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True, track_visibility='onchange'),
        'sequence': fields.integer('Sequence'),
        'type': fields.selection(CALCULATION_RULE_AVAILABLE_TYPES, 'Amount Type', required=True, track_visibility='onchange'),
        'calculation_method_id': fields.many2one('calculation.method', 'Calculation Method', select=True),
        'retrocession_id': fields.many2one('retrocession', 'Retrocession', select=True),
        'sta_mandate_id': fields.many2one('sta.mandate', 'State Mandate', select=True),
        'ext_mandate_id': fields.many2one('ext.mandate', 'External Mandate', select=True),
        'percentage': fields.float('Percentage', required=True, track_visibility='onchange', digits_compute=dp.get_precision('Percentage')),
        'amount': fields.float('Amount', track_visibility='onchange', digits_compute=dp.get_precision('Account')),
        'amount_subtotal': fields.function(_compute_subtotal, string='Subtotal', type='float', store=False, digits_compute=dp.get_precision('Account')),
        'is_deductible': fields.boolean('To deduct')
    }

    _defaults = {
        'type': 'variable',
        'is_deductible': False,
    }
    _order = 'calculation_method_id, sequence, name'

# constraints

    _unicity_keys = 'N/A'

    _constraints = [
        (_check_percentage, _("Percentage must be positive for a deductible rule."), ['percentage', 'is_deductible'])
    ]

    _sql_constraints = [
        ('positive_amount', 'check(amount >= 0.0)', 'Amount of rule must be positive.')
    ]

    def get_copy_fields_value(self, cr, uid, rule, context=None):
        """
        ==============================
        _get_rule_to_copy_fields_value
        ==============================
        Get dictionary of fields to copy for rule
        :rparam: dictionary of fields
        :rtype: dict
        """
        return dict(name=rule.name,
                    type=rule.type,
                    percentage=rule.percentage,
                    is_deductible=rule.is_deductible,
                    amount=rule.amount)


class retrocession(orm.Model):
    _name = 'retrocession'
    _description = 'Retrocession'
    _inherit = ['abstract.ficep.model']

    _inactive_cascade = True

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

    def _compute_amount(self, cr, uid, retrocessions_to_compute, rule_column, context=None):
        """
        =================
        _compute_amount
        =================
        Get computation of retrocession coming from rules
        :rparam:  retrocession amount
        :rtype: float
        """
        res = {}
        for retrocession in retrocessions_to_compute:
            res[retrocession.id] = sum([rule.amount_subtotal for rule in retrocession[rule_column]])
        return res

    def _compute_all_amounts(self, cr, uid, ids, fname, arg, context=None):
        """
        =====================
        _compute_all_amounts
        =====================
        Get total amounts of retrocession coming from fixed rules linked to mandate and variable rules
        :rparam: Retrocession amounts
        :rtype: float
        """
        res = {}
        retrocessions_to_compute = self.browse(cr, uid, ids, context=context)
        retrocede_amounts = self._compute_amount(cr, uid, retrocessions_to_compute, 'rule_ids', context=context)
        deductible_amounts = self._compute_amount(cr, uid, retrocessions_to_compute, 'deductible_rule_ids', context=context)
        for retro in retrocessions_to_compute:
            amounts = {}
            amount_total = (retrocede_amounts[retro.id] + deductible_amounts[retro.id])
            amounts['amount_retrocession'] = retrocede_amounts[retro.id] or False
            amounts['amount_deduction'] = deductible_amounts[retro.id] or False
            amounts['amount_total'] = amount_total
            amounts['amount_topay'] = amount_total - retro.provision
            res[retro.id] = amounts
        return res

    def _need_account_management(self, cr, uid, ids, fname, arg, context=None):
        """
        ========================
        _need_account_management
        ========================
        Determine whether retrocession need account management or not
        :rparam: True if accounting management needed otherwise False
        :rtype: Boolean
        """
        res = {}
        for retro in self.browse(cr, uid, ids, context=context):
            bVal = False
            if retro.retrocession_mode != 'none':
                if retro.sta_mandate_id:
                    key = 'sta_mandate_id'
                else:
                    key = 'ext_mandate_id'

                if retro[key].retro_instance_id.id == self.pool.get('int.instance').get_default(cr, uid, context=context):
                    bVal = True

            res[retro.id] = bVal

        return res

    def _get_retrocession_mode(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _get_retrocession_mode
        =================
        Get retrocession_mode linked to mandate
        :rparam: retrocession mode
        :rtype: String
        """
        res = {}
        for retrocession in self.browse(cr, uid, ids, context=context):
            res[retrocession.id] = retrocession.sta_mandate_id.retrocession_mode if retrocession.sta_mandate_id else retrocession.ext_mandate_id.retrocession_mode
        return res

    def _get_calculation_rule(self, cr, uid, ids, context=None):
        retrocession_ids = []
        retro_pool = self.pool.get('retrocession')
        for rule in self.browse(cr, uid, ids, context=context):
            if rule.retrocession_id:
                retrocession_ids.append(rule.retrocession_id.id)
            elif rule.ext_mandate_id:
                retrocession_ids += retro_pool.search(cr, uid, [('ext_mandate_id', '=', rule.ext_mandate_id.id)], context=context)
            elif rule.sta_mandate_id:
                retrocession_ids += retro_pool.search(cr, uid, [('sta_mandate_id', '=', rule.sta_mandate_id.id)], context=context)

        res = list(set(retrocession_ids))
        return res

    _amount_store_trigger = {
        'retrocession': (lambda self, cr, uid, ids, context=None: ids, ['rule_ids', 'deductible_rule_ids', 'provision'], 20),
        'calculation.rule': (_get_calculation_rule, ['amount', 'percentage'], 20),
    }

    def _get_defaults_account(self, cr, uid, ids, fname, arg, context=None):
        """
        ========================
        _get_defaults_account
        ========================
        Return all account needed for accounting moves
        :rparam: Accounts link
        :rtype: Many2one
        """
        res = {}
        for retro in self.browse(cr, uid, ids, context=None):
            if retro.sta_mandate_id:
                key = "sta_mandate_id"
            else:
                key = "ext_mandate_id"

            res[retro.id] = dict(default_credit_account=retro[key].mandate_category_id.property_retrocession_account.id or False,
                                 default_debit_account=retro[key].mandate_category_id.property_retrocession_cost_account.id or False)
        return res

    def _generate_account_move(self, cr, uid, retrocession, context=None):
        """
        ======================
        _generate_account_move
        ======================
        Generate account move for retrocession(s)
        :rparam: None
        :rtype: None
        """
        retro_journal_ids = self.pool.get('account.journal').search(cr, uid, [('code', '=', 'RETRO')], context=context)
        if not retro_journal_ids:
            retro_journal_ids = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'sale')], context=context)

        retro_journal_id = retro_journal_ids[0]
        retro_journal = self.pool.get('account.journal').browse(cr, uid, retro_journal_id, context=context)
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')

        reference = retrocession.sta_mandate_id.reference if retrocession.sta_mandate_id else retrocession.ext_mandate_id.reference

        month = retrocession.month if retrocession.month else 12

        date_str = '{day}{month}{year}'.format(day=31 if month == '12' else '01',
                                               month=month,
                                               year=retrocession.year)
        date_account_move = datetime.strptime(date_str, '%d%m%Y')

        move_vals = move_obj.account_move_prepare(cr, uid, retro_journal.id, date=date_account_move, ref=reference, context=context)

        move_id = move_obj.create(cr, uid, move_vals, context=context)

        line_vals = dict(name=retrocession.unique_id,
                           partner_id=retrocession.partner_id.id,
                           account_id=False,
                           debit=0,
                           credit=0,
                           move_id=move_id)

        if retrocession.amount_deduction < 0:
            line_vals['credit'] = 0
            line_vals['debit'] = -retrocession.amount_deduction
            if retrocession.default_debit_account:
                line_vals['account_id'] = retrocession.default_debit_account.id
            else:
                raise orm.except_orm(_('Error!'), _('Please set a retrocession costs account on mandate category.'))

            move_line_obj.create(cr, uid, line_vals)

        line_vals['credit'] = retrocession.amount_retrocession
        line_vals['debit'] = 0
        if retrocession.default_credit_account:
            line_vals['account_id'] = retrocession.default_credit_account.id
        else:
            raise orm.except_orm(_('Error!'), _('Please set a retrocession account on mandate category.'))
        move_line_obj.create(cr, uid, line_vals)

        line_vals['credit'] = 0
        line_vals['debit'] = retrocession.amount_total
        line_vals['account_id'] = retro_journal.default_debit_account_id.id
        move_line_obj.create(cr, uid, line_vals)

        self.write(cr, uid, retrocession.id, {'move_id': move_id}, context=context)
        move_obj.post(cr, uid, [move_id], context=context)

    _columns = {
        'unique_id': fields.char('Number of retrocession'),
        'state': fields.selection(RETROCESSION_AVAILABLE_STATES, 'State', size=128, required=True, select=True, track_visibility='onchange'),
        'sta_mandate_id': fields.many2one('sta.mandate', 'State Mandate', select=True),
        'ext_mandate_id': fields.many2one('ext.mandate', 'External Mandate', select=True),
        'partner_id': fields.function(_get_partner_id, string='Representative',
                                 type='many2one', relation='res.partner', store=False),
        'retrocession_mode': fields.function(_get_retrocession_mode, string='Retrocession Mode',
                                 type='selection', selection=RETROCESSION_MODES_AVAILABLE, store=False),
        'month': fields.selection(fields.date.MONTHS, 'Month', select=True, track_visibility='onchange'),
        'year': fields.char('Year', size=128, select=True, track_visibility='onchange'),
        'rule_ids': fields.one2many('calculation.rule', 'retrocession_id', 'Calculation Rules', domain=[('active', '=', True), ('is_deductible', '=', False)]),
        'rule_inactive_ids': fields.one2many('calculation.rule', 'retrocession_id', 'Calculation Rules', domain=[('active', '=', False), ('is_deductible', '=', False)]),
        'deductible_rule_ids': fields.one2many('calculation.rule', 'retrocession_id', 'Deductible Calculation Rules', domain=[('active', '=', True), ('is_deductible', '=', True)]),
        'deductible_rule_inactive_ids': fields.one2many('calculation.rule', 'retrocession_id', 'Deductible Calculation Rules', domain=[('active', '=', False), ('is_deductible', '=', True)]),
        'amount_retrocession': fields.function(_compute_all_amounts, string='Amount to Retrocede', multi="Allamounts",
                                 type='float', store=_amount_store_trigger, digits_compute=dp.get_precision('Account')),
        'amount_deduction': fields.function(_compute_all_amounts, string='Amount deductible', multi="Allamounts",
                                 type='float', store=_amount_store_trigger, digits_compute=dp.get_precision('Account')),
        'amount_total': fields.function(_compute_all_amounts, string='Total', multi="Allamounts",
                                        type='float', store=_amount_store_trigger, digits_compute=dp.get_precision('Account')),
        'amount_topay': fields.function(_compute_all_amounts, string='To Pay', multi="Allamounts",
                                        type='float', store=_amount_store_trigger, digits_compute=dp.get_precision('Account')),
        'amount_paid': fields.float('Amount Paid'),
        'move_id': fields.many2one('account.move', 'Journal Entry', select=True),
        'need_account_management': fields.function(_need_account_management, string='Need accounting management', type='boolean', store=False),
        'default_debit_account': fields.function(_get_defaults_account, string="Default debit account", type="many2one", relation='account.account', store=False, multi="All_accounts"),
        'default_credit_account': fields.function(_get_defaults_account, string="Default credit account", type="many2one", relation='account.account', store=False, multi="All_accounts"),
        'is_regulation': fields.boolean('Regulation Retrocession ?'),
        'provision': fields.float('Provision', digits_compute=dp.get_precision('Account')),
    }

    _order = 'year desc, month desc, sta_mandate_id, ext_mandate_id'

    _defaults = {
        'state': 'draft',
        'is_regulation': False
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
            nb_retro = len(self.search(cr, uid, [(key, '=', retro[key].id),
                                                 ('id', '!=', retro.id),
                                                 ('month', '=', retro.month),
                                                 ('year', '=', retro.year),
                                                 ('is_regulation', '=', False)], context=context))

            if nb_retro > 0:
                if int(retro.month) != 12:
                    return False
                else:
                    if retro.is_regulation:
                        if len(self.search(cr, uid, [(key, '=', retro[key].id),
                                                             ('id', '!=', retro.id),
                                                             ('month', '=', retro.month),
                                                             ('year', '=', retro.year),
                                                             ('is_regulation', '=', True)], context=context)) > 0:
                            return False
                    else:
                        return False

        return True

    def _check_value(self, cr, uid, ids, for_unlink=False, context=None):
        """
        =================
        _check_value
        =================
        Check if retrocession amount is positive
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        for retro in self.browse(cr, uid, ids):
            if retro.state == 'validated' and retro.amount_total < 0:
                return False

        return True

    def _check_regulation(self, cr, uid, ids, for_unlink=False, context=None):
        """
        =================
        _check_regulation
        =================
        A regulation retrocession should only occur on December
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        for retro in self.browse(cr, uid, ids):
            if retro.is_regulation and int(retro.month) != 12:
                return False

        return True

    def _check_paid(self, cr, uid, ids, for_unlink=False, context=None):
        """
        =================
        _check_paid
        =================
        A paid retrocession should have a non-zero paid amount
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        for retro in self.browse(cr, uid, ids):
            if retro.state == 'paid' and retro.amount_paid == 0:
                return False

        return True

    _constraints = [
        (_check_unicity, _("A retrocession already exists for this mandate at this period"), ['sta_mandate_id', 'ext_mandate_id']),
        (_check_value, _("You can not validate a negative retrocession"), ['amount_total']),
        (_check_regulation, _("A regulation retrocession should only occur on December"), ['is_regulation']),
        (_check_paid, _("No amount paid specified."), ['state'])
    ]

    _unicity_keys = 'N/A'

# orm methods

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

            for rule in mandate_rec.rule_ids:
                data = self.pool['calculation.rule'].get_copy_fields_value(cr, uid, rule)
                data['retrocession_id'] = retro.id
                self.pool['calculation.rule'].create(cr, uid, data, context=context)

            for rule in mandate_rec.deductible_rule_ids:
                data = self.pool['calculation.rule'].get_copy_fields_value(cr, uid, rule)
                data['retrocession_id'] = retro.id
                self.pool['calculation.rule'].create(cr, uid, data, context=context)

        return res

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []
        for retro in self.browse(cr, uid, ids, context=context):
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
                translator = self.browse(cr, uid, retro.id, context=context, fields_process=translate_selections)
                display_name = u'{mandate} ({month} {year})'.format(month=translator.month,
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
            retrocession_mode = self.pool.get('sta.mandate').read(cr, uid, sta_mandate_id, ['retrocession_mode'], context=context)['retrocession_mode']
            res['value'] = dict(retrocession_mode=retrocession_mode or False)

        return res

    def onchange_ext_mandate_id(self, cr, uid, ids, ext_mandate_id, context=None):
        res = {}
        if ext_mandate_id:
            retrocession_mode = self.pool.get('ext.mandate').read(cr, uid, ext_mandate_id, ['retrocession_mode'], context=context)['retrocession_mode']
            res['value'] = dict(retrocession_mode=retrocession_mode or False)

        return res

    def button_dummy(self, cr, uid, retro_id, context=None):
        return True

    def action_validate(self, cr, uid, ids, context=None):
        """
        =================
        action_validate
        =================
        Change state of retrocession to 'Validated' and generate account move if needed
        :rparam: False
        :rtype: Boolean
        """
        self.write(cr, uid, ids, {'state': 'validated'}, context=context)
        # copy fixed rules on retrocession to keep history of calculation basis
        for retrocession in self.browse(cr, uid, ids, context=context):
            if not retrocession.unique_id:
                retro_number = '{mandate}/{year}{month}{regulation}'.format(mandate=retrocession.sta_mandate_id.unique_id if retrocession.sta_mandate_id else retrocession.ext_mandate_id.unique_id,
                                                                year=retrocession.year,
                                                                month=str(retrocession.month).rjust(2, '0') if retrocession.month else "00",
                                                                regulation='1' if retrocession.is_regulation else '0')
                self.write(cr, uid, retrocession.id, {'unique_id': retro_number}, context=context)
                retrocession = self.browse(cr, uid, retrocession.id, context=context)

            if retrocession.need_account_management and retrocession.amount_total > 0:
                self._generate_account_move(cr, uid, retrocession, context)
            # TODO: send report to mandate representative and return its id
        return False

    def action_invalidate(self, cr, uid, ids, context=None, vals=None):
        """
        =================
        action_invalidate
        =================
        Cancel a Retrocession
        """
        vals = vals or {}
        vals.update({'state': 'cancelled'})
        account_move_ids = [retro_data['move_id'][0] for retro_data in self.read(cr, uid, ids, ['move_id'], context=context) if retro_data['move_id']]
        self.pool.get('account.move').button_cancel(cr, uid, account_move_ids, context=context)
        self.pool.get('account.move').unlink(cr, uid, account_move_ids, context=context)
        return super(retrocession, self).action_invalidate(cr, uid, ids, context=context, vals=vals)

    def action_revalidate(self, cr, uid, ids, context=None, vals=None):
        """
        =================
        action_revalidate
        =================
        Reset Retrocession to draft state unlinking generated fixed rules
        """
        vals = vals or {}
        vals.update({'state': 'draft'})
        res = super(retrocession, self).action_revalidate(cr, uid, ids, context=context, vals=vals)
        account_move_ids = [retro_data['move_id'][0] for retro_data in self.read(cr, uid, ids, ['move_id'], context=context) if retro_data['move_id']]
        self.pool.get('account.move').button_cancel(cr, uid, account_move_ids, context=context)
        self.pool.get('account.move').unlink(cr, uid, account_move_ids, context=context)
        return res

    def action_paid(self, cr, uid, ids, context=None, vals=None):
        """
        =================
        action_paid
        =================
        Mark a retrocession as paid
        """
        self.write(cr, uid, ids, {'state': 'paid'}, context=context)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
