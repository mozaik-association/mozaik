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

from datetime import datetime

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import SUPERUSER_ID
import openerp.addons.decimal_precision as dp

from .common import RETROCESSION_MODES_AVAILABLE, \
    CALCULATION_METHOD_AVAILABLE_TYPES, CALCULATION_RULE_AVAILABLE_TYPES
from openerp.exceptions import except_orm

RETROCESSION_AVAILABLE_STATES = [
    ('draft', 'Open'),
    ('validated', 'Validated'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled'),
]


class fractionation(orm.Model):
    _name = 'fractionation'
    _description = 'Fractionation'
    _inherit = ['mozaik.abstract.model']

    _inactive_cascade = True

    def _compute_total_percentage(self, cr, uid, ids, fname, arg,
                                  context=None):
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
            if fractionation.active:
                lines = fractionation.fractionation_line_ids
            else:
                lines = fractionation.fractionation_line_inactive_ids
            res[fractionation.id] = sum([line.percentage for line in lines])
        return res

    _total_percentage_store_trigger = {
        'fractionation': (
            lambda self, cr, uid, ids, context=None: ids, [
                'fractionation_line_ids', 'active'], 20),
        'fractionation.line': (
            lambda self, cr, uid, ids, context=None: [
                line_data['fractionation_id'][0] for line_data in self.read(
                    cr, uid, ids, ['fractionation_id'], context=context)], [
                'percentage', 'active', ], 20), }

    _columns = {
        'name': fields.char(
            'Name',
            size=128,
            required=True,
            select=True,
            track_visibility='onchange'),
        'mandate_category_ids': fields.one2many(
            'mandate.category',
            'fractionation_id',
            'Mandate Categories'),
        'fractionation_line_ids': fields.one2many(
            'fractionation.line',
            'fractionation_id',
            'Fractionation Lines',
            domain=[
                ('active',
                 '=',
                 True)]),
        'fractionation_line_inactive_ids': fields.one2many(
            'fractionation.line',
            'fractionation_id',
            'Fractionation Lines',
            domain=[
                ('active',
                 '=',
                 False)]),
        'total_percentage': fields.function(
            _compute_total_percentage,
            string='Total Percentage',
            type='float',
            store=_total_percentage_store_trigger,
            digits_compute=dp.get_precision('Percentage')),
    }

    _order = 'name'

# constraints

    _unicity_keys = 'name'

# orm methods

    def copy_data(self, cr, uid, id_, default=None, context=None):
        res = super(
            fractionation,
            self).copy_data(
            cr,
            uid,
            id_,
            default=default,
            context=context)

        res.update({
            'name': _('%s (copy)') % res.get('name'),
        })
        return res


class fractionation_line(orm.Model):
    _name = 'fractionation.line'
    _description = 'Fractionation Line'
    _inherit = ['mozaik.abstract.model']

    _columns = {
        'fractionation_id': fields.many2one(
            'fractionation',
            'Fractionation',
            required=True,
            select=True,
            track_visibility='onchange'),
        'power_level_id': fields.many2one(
            'int.power.level',
            'Internal Power Level',
            required=True,
            select=True,
            track_visibility='onchange'),
        'percentage': fields.float(
            'Percentage',
            required=True,
            track_visibility='onchange',
            digits_compute=dp.get_precision('Percentage'))}

    _order = 'fractionation_id, power_level_id'

    _rec_name = 'power_level_id'

# constraints

    _unicity_keys = 'fractionation_id, power_level_id'

    _sql_constraints = [
        ('lessthan100_line',
         'check(0.0 < percentage and percentage <= 100.0)',
         'Percentage should be greater than zero and lower or equal to 100 %')]


class calculation_method(orm.Model):
    _name = 'calculation.method'
    _description = 'Calculation Method'
    _inherit = ['mozaik.abstract.model']

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
            rule_ids = calculation_method.calculation_rule_ids
            rule_types = list(
                set([rules.type for rules in rule_ids]))
            res[calculation_method.id] = rule_types[
                0] if len(rule_types) == 1 else 'mixed'
        return res

    def _calculation_rule(self, cr, uid, ids, context=None):
        rule_datas = self.pool['calculation.rule'].read(
            cr, uid, ids, ['calculation_method_id'], context=context)
        vals = []
        for data in rule_datas:
            if data['calculation_method_id']:
                vals.append(data['calculation_method_id'][0])
        return vals

    _type_store_trigger = {
        'calculation.method': (
            lambda self, cr, uid, ids, context=None: ids,
            ['calculation_rule_ids'], 20),
        'calculation.rule': (_calculation_rule,
                             ['type', ], 20), }

    _columns = {
        'name': fields.char(
            'Name',
            size=128,
            required=True,
            select=True,
            track_visibility='onchange'),
        'type': fields.function(
            _get_method_type,
            string='Type',
            type='selection',
            store=_type_store_trigger,
            select=True,
            selection=CALCULATION_METHOD_AVAILABLE_TYPES),
        'calculation_rule_ids': fields.one2many(
            'calculation.rule',
            'calculation_method_id',
            'Calculation Rules'),
        'mandate_category_ids': fields.one2many(
            'mandate.category',
            'calculation_method_id',
            'Mandate Categories'),
    }

    _order = 'name'

# constraints

    _unicity_keys = 'name'

# public methods

    def copy_fixed_rules_on_mandate(
            self,
            cr,
            uid,
            method_id,
            mandate_id,
            mandate_key,
            context=None):
        """
        ===========================
        copy_fixed_rules_on_mandate
        ===========================
        copy all fixed linked to method on given mandate
        :rparam: result
        :rtype: Boolean
        """
        rule_pool = self.pool.get('calculation.rule')
        rule_ids = rule_pool.search(
            cr, uid, [
                (mandate_key, '=', mandate_id),
                ('type', '=', 'fixed')],
            context=context)
        if rule_ids:
            rule_pool.unlink(cr, uid, rule_ids, context=context)

        if method_id:
            rule_ids = rule_pool.search(
                cr, uid, [
                    ('calculation_method_id', '=', method_id),
                    ('type', '=', 'fixed')],
                context=context)
            for rule in rule_pool.browse(cr, uid, rule_ids, context=context):
                data = rule_pool.get_copy_fields_value(cr, uid, rule)
                data[mandate_key] = mandate_id
                rule_pool.create(cr, uid, data, context=context)

        return True

    def copy_variable_rules_on_retrocession(
            self,
            cr,
            uid,
            method_id,
            retrocession_id,
            context=None):
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
            rule_ids = rule_pool.search(
                cr, uid, [
                    ('calculation_method_id', '=', method_id),
                    ('type', '=', 'variable')],
                context=context)
            for rule in rule_pool.browse(cr, uid, rule_ids, context=context):
                data = rule_pool.get_copy_fields_value(cr, uid, rule)
                data['retrocession_id'] = retrocession_id
                rule_pool.create(cr, uid, data, context=context)

        return True


class calculation_rule(orm.Model):
    _name = 'calculation.rule'
    _description = 'Calculation Rule'
    _inherit = ['mozaik.abstract.model']

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
        uid = SUPERUSER_ID
        for rule in self.browse(cr, uid, ids, context=context):
            return False if (
                rule.is_deductible and rule.percentage < 0) else True

    _columns = {
        'name': fields.char(
            'Name',
            size=128,
            required=True,
            select=True,
            track_visibility='onchange'),
        'sequence': fields.integer('Sequence', group_operator='min'),
        'type': fields.selection(
            CALCULATION_RULE_AVAILABLE_TYPES,
            'Amount Type',
            required=True,
            track_visibility='onchange'),
        'calculation_method_id': fields.many2one(
            'calculation.method',
            'Calculation Method',
            select=True),
        'retrocession_id': fields.many2one(
            'retrocession',
            'Retrocession',
            select=True),
        'sta_mandate_id': fields.many2one(
            'sta.mandate',
            'State Mandate',
            select=True),
        'ext_mandate_id': fields.many2one(
            'ext.mandate',
            'External Mandate',
            select=True),
        'percentage': fields.float(
            'Percentage',
            required=True,
            track_visibility='onchange',
            digits_compute=dp.get_precision('Percentage')),
        'amount': fields.float(
            'Amount',
            track_visibility='onchange',
            digits_compute=dp.get_precision('Account')),
        'amount_subtotal': fields.function(
            _compute_subtotal,
            string='Subtotal',
            type='float',
            store=False,
            digits_compute=dp.get_precision('Account')),
        'is_deductible': fields.boolean('To deduct')}

    _defaults = {
        'type': 'variable',
        'is_deductible': False,
    }
    _order = 'calculation_method_id, sequence, name'

# constraints

    _unicity_keys = 'N/A'

    _constraints = [
        (_check_percentage,
         _("Percentage must be positive for a deductible rule."), [
             'percentage', 'is_deductible'])]

    _sql_constraints = [
        ('positive_amount',
         'check(amount >= 0.0)',
         'Amount of rule must be positive.')]

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
    _inherit = ['mozaik.abstract.model']

    _inactive_cascade = True

    def _get_account_amount(self, cr, uid, retro, context=None):
        provision = 0.0
        amount_paid = 0.0
        amount_reconcilied = 0.0

        if not retro.month:
            bsl_obj = self.pool.get('account.bank.statement.line')
            aml_obj = self.pool.get('account.move.line')
            domain = [('name', '=', retro.mandate_ref.reference),
                      ('partner_id', '=', retro.partner_id.id)]
            bsl_data = bsl_obj.search_read(cr,
                                           uid,
                                           domain,
                                           fields=['journal_entry_id',
                                                   'amount'],
                                           context=context)
            for provision_data in bsl_data:
                b_sum = True
                if provision_data['journal_entry_id']:
                    domain = [('move_id', '=',
                               provision_data['journal_entry_id'][0]),
                              '|', ('reconcile_id', '!=', False),
                              ('reconcile_partial_id', '!=', False)]
                    if len(aml_obj.search(cr, uid, domain, context=None)) > 0:
                        b_sum = False

                if b_sum:
                    provision += float(provision_data['amount'])

        query = """ SELECT distinct aml.reconcile_id, aml.reconcile_partial_id
                      FROM account_move_line aml
                      LEFT JOIN account_move am    on am.id       = aml.move_id
                      LEFT JOIN retrocession r     on aml.move_id = r.move_id
                      LEFT JOIN account_journal aj on am.journal_id = aj.id
                    WHERE r.id = %s
                     AND aml.account_id = aj.default_debit_account_id
                """
        cr.execute(query, (retro.id,))
        data = cr.fetchone()
        if data:
            reconcile_id = data[0]
            reconcile_partial_id = data[1]
            where_clause, values = False, False
            if reconcile_id:
                where_clause = 'aml.reconcile_id = %s'
                values = (reconcile_id,)
            elif reconcile_partial_id:
                where_clause = 'aml.reconcile_partial_id = %s'
                values = (reconcile_partial_id,)

            if where_clause:
                query = """
                    SELECT line.debit,
                           line.credit,
                           line.account_id,
                           aa.type
                      FROM account_move_line aml
                      JOIN account_move_line line ON line.move_id = aml.move_id
                      JOIN account_journal aj     ON line.journal_id = aj.id
                      JOIN account_account aa     ON aa.id = line.account_id
                     WHERE %s
                       AND aj.type= 'bank'
                    """ % where_clause
                cr.execute(query, values)
                data = [line for line in cr.fetchall()]
                amount_paid = 0
                amount_reconcilied = 0
                for line in data:
                    if line[3] == 'liquidity':
                        amount_paid = amount_paid + line[0] - line[1]

                    if line[3] == 'receivable':
                        amount_reconcilied = amount_reconcilied - line[0]\
                            + line[1]

        return provision, amount_reconcilied, amount_paid

    def _compute_all_amounts(self, cr, uid, ids, fname, arg, context=None):
        """
        =====================
        _compute_all_amounts
        =====================
        Get total amounts of retrocession coming from fixed rules linked to
        mandate and variable rules
        :rparam: Retrocession amounts
        :rtype: float
        """
        res = {}
        for retro in self.browse(cr, uid, ids, context=context):
            rule_ids = []
            deductible_rule_ids = []
            if retro.active:
                rule_ids = retro.rule_ids
                deductible_rule_ids = retro.deductible_rule_ids
            else:
                rule_ids = retro.rule_inactive_ids
                deductible_rule_ids = retro.deductible_rule_inactive_ids

            amount_retrocession = sum([rule.amount_subtotal
                                       for rule in rule_ids])
            amount_deduction = sum([rule.amount_subtotal
                                    for rule in deductible_rule_ids])
            amount_total = (amount_retrocession + amount_deduction)
            provision = retro.provision
            amount_reconcilied = 0.0
            amount_paid = retro.amount_paid
            if retro.need_account_management:
                amounts = self._get_account_amount(cr, uid, retro, context)
                provision = amounts[0]
                amount_reconcilied = amounts[1]
                amount_paid = amounts[2]
            amount_due = amount_total - provision - amount_reconcilied
            res[retro.id] = dict(provision=provision,
                                 amount_retrocession=amount_retrocession,
                                 amount_deduction=amount_deduction,
                                 amount_total=amount_total,
                                 amount_due=amount_due,
                                 amount_reconcilied=amount_reconcilied,
                                 amount_paid=amount_paid)
        return res

    def _get_calculation_rule(self, cr, uid, ids, context=None):
        retrocession_ids = []
        retro_pool = self.pool.get('retrocession')
        for rule in self.browse(cr, uid, ids, context=context):
            if rule.retrocession_id:
                retrocession_ids.append(rule.retrocession_id.id)
            elif rule.ext_mandate_id:
                retrocession_ids += retro_pool.search(
                    cr,
                    uid,
                    [('ext_mandate_id',
                      '=',
                      rule.ext_mandate_id.id)],
                    context=context)
            elif rule.sta_mandate_id:
                retrocession_ids += retro_pool.search(
                    cr,
                    uid,
                    [('sta_mandate_id',
                      '=',
                      rule.sta_mandate_id.id)],
                    context=context)

        res = list(set(retrocession_ids))
        return res

    def _get_bank_statement_line(self, cr, uid, ids, context=None):
        retrocession_ids = []
        retro_pool = self.pool.get('retrocession')
        for line in self.browse(cr, uid, ids, context=context):
            mandate_ids = []
            mandate = False
            if line.name:
                domain = [('reference', '=', line.name)]
                mandate = 'sta.mandate'
                mandate_ids = self.pool.get(mandate).search(
                    cr,
                    uid,
                    domain,
                    context=context)
                if not mandate_ids:
                    mandate = 'ext.mandate'
                    mandate_ids = self.pool.get('ext.mandate').search(
                        cr,
                        uid,
                        domain,
                        context=context)

            if mandate_ids:
                domain = [
                    (retro_pool.get_relation_column_name(
                        cr,
                        uid,
                        mandate,
                        context=context),
                        'in',
                        mandate_ids),
                    ('active',
                     '<=',
                     True)]
                retrocession_ids += retro_pool.search(cr,
                                                      uid,
                                                      domain,
                                                      context=context)

        res = list(set(retrocession_ids))
        return res

    def _get_account_move_line(self, cr, uid, ids, context=None):
        retrocession_ids = []
        retro_pool = self.pool.get('retrocession')
        for line in self.browse(cr, uid, ids, context=context):
            retro_ids = retro_pool.search(
                cr, uid, [
                    ('move_id', '=', line.move_id.id),
                    ('active', '<=', True)],
                context=context)
            domain = []
            if not retro_ids and line.reconcile_id:
                domain = [('reconcile_id', '=', line.reconcile_id.id)]
            elif not retro_ids and line.reconcile_partial_id:
                domain = [
                    ('reconcile_partial_id',
                     '=',
                     line.reconcile_partial_id.id)]

            if domain:
                line_ids = self.search(cr, uid, domain, context=context)
                for move_line in self.browse(
                        cr,
                        uid,
                        line_ids,
                        context=context):
                    retro_ids += retro_pool.search(cr,
                                                   uid,
                                                   [('move_id',
                                                     '=',
                                                     move_line.move_id.id),
                                                    ('active',
                                                     '<=',
                                                     True)],
                                                   context=context)

            retrocession_ids += retro_ids

        res = list(set(retrocession_ids))
        return res

    _amount_store_trigger = {
        'retrocession': (lambda self, cr, uid, ids, context=None:
                         ids, ['rule_ids', 'deductible_rule_ids'], 20),
        'calculation.rule': (_get_calculation_rule, ['amount', 'percentage'],
                             20),
        'account.bank.statement.line': (_get_bank_statement_line,
                                        ['amount', 'name', 'journal_entry_id',
                                         'partner_id'], 20),
        'account.move.line': (_get_account_move_line,
                              ['reconcile_id', 'reconcile_partial_id'], 20)
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
            category_id = retro.mandate_ref.mandate_category_id
            res[retro.id] = {
                'default_credit_account':
                    category_id.property_retrocession_account.id,
                'default_debit_account':
                    category_id.property_retrocession_cost_account.id
            }
        return res

    def _get_coordinate(self, cr, uid, ids, model, foreign_key, context=None):
        """
        ========================
        _get_coordinate
        ========================
        Return coordinate for representative
        :rparam: Coordinate link
        :rtype: Many2one
        """
        res = {}
        for retro in self.browse(cr, uid, ids, context=None):
            coordinate_id = False
            if retro.mandate_ref[foreign_key]:
                coordinate_id = retro.mandate_ref[foreign_key].id
            else:
                coordinate_ids = self.pool.get(model).search(
                    cr, uid, [
                        ('partner_id', '=', retro.partner_id.id),
                        ('is_main', '=', True)],
                    context=context)
                if coordinate_ids:
                    coordinate_id = coordinate_ids[0]
            res[retro.id] = coordinate_id
        return res

    def _get_postal_coordinate(self, cr, uid, ids, fname, arg, context=None):
        """
        ========================
        _get_postal_coordinate
        ========================
        Return postal coordinate for representative
        :rparam: Email coordinate link
        :rtype: Many2one
        """
        return self._get_coordinate(
            cr,
            uid,
            ids,
            'postal.coordinate',
            'postal_coordinate_id',
            context=context)

    def _get_email_coordinate(self, cr, uid, ids, fname, arg, context=None):
        """
        ========================
        _get_email_coordinate
        ========================
        Return email coordinate for representative
        :rparam: Email coordinate link
        :rtype: Many2one
        """
        return self._get_coordinate(
            cr,
            uid,
            ids,
            'email.coordinate',
            'email_coordinate_id',
            context=context)

    def _accept_anyway(self, cr, uid, ids, name, value, args, context=None):
        '''
        Accept the modification of the provision
        Do not make a self.write here, it will indefinitely loop on itself...
        '''
        cr.execute(
            'update %s set %s = %%s where id = %s' %
            (self._table, name, ids), (value or None,))
        return True

    def _get_document_types(self, cr, uid, context=None):
        cr.execute(
            "SELECT model, name from ir_model WHERE model "
            "IN ('sta.mandate', 'ext.mandate') ORDER BY name")
        return cr.fetchall()

    def _get_retrocessions(self, cr, uid, partner_ids, context=None):
        """
        Return retrocessions ids associated to a list of partners
        """
        query = """
            SELECT r.id
              FROM generic_mandate g, retrocession r
             WHERE g.model = 'sta.mandate'
               AND g.partner_id IN %s
               AND r.sta_mandate_id = g.mandate_id
            UNION
            SELECT r.id
              FROM generic_mandate g, retrocession r
             WHERE g.model = 'ext.mandate'
               AND g.partner_id IN %s
               AND r.ext_mandate_id = g.mandate_id"""
        ids = tuple(partner_ids)
        cr.execute(query, (ids, ids,))
        r_ids = [x[0] for x in cr.fetchall()]
        return r_ids

    def _get_partner_instance_id(self, cr, uid, ids, name, args, context=None):
        """
        Recompute partner instance id associated to retrocession ids
        """
        query = """
            SELECT r.id, g.partner_instance_id
              FROM retrocession r, generic_mandate g
             WHERE r.id IN %s
               AND g.mandate_ref = r.mandate_ref"""
        cr.execute(query, (tuple(ids),))
        res = {x[0]: x[1] for x in cr.fetchall()}
        return res

    def _get_retro_instance_id(self, cr, uid, ids, name, args, context=None):
        """
        Recompute retro instance id associated to retrocession ids
        """
        query = """
            SELECT r.id, m.retro_instance_id
              FROM retrocession r, sta_mandate m
             WHERE r.id IN %s
               AND m.id = r.sta_mandate_id
            UNION
            SELECT r.id, m.retro_instance_id
              FROM retrocession r, ext_mandate m
             WHERE r.id IN %s
               AND m.id = r.ext_mandate_id"""
        r_ids = tuple(ids)
        cr.execute(query, (r_ids, r_ids,))
        res = {x[0]: x[1] for x in cr.fetchall()}
        return res

    _int_instance_store_trigger = {
        'retrocession': (lambda self, cr, uid, ids, context=None: ids,
                         ['sta_mandate_id', 'ext_mandate_id'], 10),
        'res.partner': (_get_retrocessions, ['int_instance_id'], 10),
    }

    _retro_instance_store_trigger = {
        'retrocession': (lambda self, cr, uid, ids, context=None: ids,
                         ['sta_mandate_id', 'ext_mandate_id'], 10),
        'sta.mandate': (lambda self, cr, uid, ids, context=None:
                        self.pool['retrocession'].search(
                            cr, SUPERUSER_ID, [('sta_mandate_id', 'in', ids)],
                            context=context),
                        ['retro_instance_id'], 10),
        'ext.mandate': (lambda self, cr, uid, ids, context=None:
                        self.pool['retrocession'].search(
                            cr, SUPERUSER_ID, [('ext_mandate_id', 'in', ids)],
                            context=context),
                        ['retro_instance_id'], 10),
    }

    _columns = {
        'unique_id': fields.char('Retrocession Number'),
        'state': fields.selection(
            RETROCESSION_AVAILABLE_STATES,
            'State',
            size=128,
            required=True,
            select=True,
            track_visibility='onchange'),
        'sta_mandate_id': fields.many2one(
            'sta.mandate',
            'State Mandate',
            select=True),
        'ext_mandate_id': fields.many2one(
            'ext.mandate',
            'External Mandate',
            select=True),
        'mandate_ref': fields.reference(
            'Mandate Reference',
            selection=_get_document_types),
        'partner_id': fields.related(
            'mandate_ref',
            'partner_id',
            string='Partner',
            type='many2one',
            relation='res.partner',
            store=False),
        'retrocession_mode': fields.related(
            'mandate_ref',
            'retrocession_mode',
            string='Retrocession Mode',
            type='selection',
            selection=RETROCESSION_MODES_AVAILABLE,
            store=False),
        'month': fields.selection(
            fields.date.MONTHS,
            'Month',
            select=True,
            track_visibility='onchange'),
        'year': fields.char(
            'Year',
            size=128,
            select=True,
            track_visibility='onchange'),
        'rule_ids': fields.one2many(
            'calculation.rule',
            'retrocession_id',
            'Calculation Rules',
            domain=[
                ('active',
                 '=',
                 True),
                ('is_deductible',
                 '=',
                 False)]),
        'rule_inactive_ids': fields.one2many(
            'calculation.rule',
            'retrocession_id',
            'Calculation Rules',
            domain=[
                ('active',
                 '=',
                 False),
                ('is_deductible',
                 '=',
                 False)]),
        'deductible_rule_ids': fields.one2many(
            'calculation.rule',
            'retrocession_id',
            'Deductible Calculation Rules',
            domain=[
                ('active',
                 '=',
                 True),
                ('is_deductible',
                 '=',
                 True)]),
        'deductible_rule_inactive_ids': fields.one2many(
            'calculation.rule',
            'retrocession_id',
            'Deductible Calculation Rules',
            domain=[
                ('active',
                 '=',
                 False),
                ('is_deductible',
                 '=',
                 True)]),
        'amount_retrocession': fields.function(
            _compute_all_amounts,
            string='Amount to Retrocede',
            multi="Allamounts",
            type='float',
            store=_amount_store_trigger,
            digits_compute=dp.get_precision('Account')),
        'amount_deduction': fields.function(
            _compute_all_amounts,
            string='Amount deductible',
            multi="Allamounts",
            type='float',
            store=_amount_store_trigger,
            digits_compute=dp.get_precision('Account')),
        'amount_total': fields.function(
            _compute_all_amounts,
            string='Total',
            multi="Allamounts",
            type='float',
            store=_amount_store_trigger,
            digits_compute=dp.get_precision('Account')),
        'amount_due': fields.function(
            _compute_all_amounts,
            string='Amount Due',
            multi="Allamounts",
            type='float',
            store=_amount_store_trigger,
            digits_compute=dp.get_precision('Account')),
        'provision': fields.function(
            _compute_all_amounts,
            string='Provision',
            type="float",
            multi="Allamounts",
            digits_compute=dp.get_precision('Account'),
            store=_amount_store_trigger,
            fnct_inv=_accept_anyway),
        'amount_reconcilied': fields.function(
            _compute_all_amounts,
            string='Amount Reconcilied',
            type="float",
            multi="Allamounts",
            digits_compute=dp.get_precision('Account'),
            store=_amount_store_trigger,
            fnct_inv=_accept_anyway),
        'amount_paid': fields.function(
            _compute_all_amounts,
            string='Amount Paid',
            type="float",
            multi="Allamounts",
            digits_compute=dp.get_precision('Account'),
            store=_amount_store_trigger,
            fnct_inv=_accept_anyway),
        'move_id': fields.many2one(
            'account.move',
            'Journal Entry',
            select=True),
        'need_account_management': fields.related(
            'mandate_ref',
            'need_account_management',
            string='Need accounting management',
            type='boolean',
            store=False),
        'default_debit_account': fields.function(
            _get_defaults_account,
            string="Default debit account",
            type="many2one",
            relation='account.account',
            store=False,
            multi="All_accounts"),
        'default_credit_account': fields.function(
            _get_defaults_account,
            string="Default credit account",
            type="many2one",
            relation='account.account',
            store=False,
            multi="All_accounts"),
        'is_regulation': fields.boolean('Regulation Retrocession?'),
        'email_date': fields.date('Last email Sent'),
        'email_coordinate_id': fields.function(
            _get_email_coordinate,
            string='Email Coordinate',
            type='many2one',
            relation='email.coordinate',
            store=False),
        'postal_coordinate_id': fields.function(
            _get_postal_coordinate,
            string='Postal Coordinate',
            type='many2one',
            relation='postal.coordinate',
            store=False),
        'partner_instance_id': fields.function(
            _get_partner_instance_id,
            string='Partner Internal Instance',
            type='many2one',
            relation='int.instance',
            select=True,
            readonly=True,
            store=_int_instance_store_trigger),
        'retro_instance_id': fields.function(
            _get_retro_instance_id,
            string='Retrocessions Management Instance',
            type='many2one',
            relation='int.instance',
            select=True,
            readonly=True,
            store=_retro_instance_store_trigger),
    }

    _rec_name = 'mandate_ref'

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
        uid = SUPERUSER_ID
        retrocessions = self.browse(cr, uid, ids)
        for retro in retrocessions:
            domain = [
                (self.get_relation_column_name(
                    cr,
                    uid,
                    retro.mandate_ref._name,
                    context=context),
                    '=',
                    retro.mandate_ref.id),
                ('id',
                 '!=',
                 retro.id),
                ('month',
                 '=',
                 retro.month),
                ('year',
                 '=',
                 retro.year),
                ('is_regulation',
                 '=',
                 False),
                ('active',
                 '<=',
                 True)]

            if len(self.search(cr, uid, domain, context=context)) > 0:
                if int(retro.month) != 12:
                    return False
                else:
                    if retro.is_regulation:
                        domain[4] = ('is_regulation', '=', True)
                        if len(
                            self.search(
                                cr,
                                uid,
                                domain,
                                context=context)) > 0:
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
        uid = SUPERUSER_ID
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
        uid = SUPERUSER_ID
        for retro in self.browse(cr, uid, ids):
            if retro.is_regulation and int(retro.month) != 12:
                return False

        return True

    def _check_paid(self, cr, uid, ids, for_unlink=False, context=None):
        """
        =================
        _check_paid
        =================
        A retrocession done should have a non-zero paid amount
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        uid = SUPERUSER_ID
        for retro in self.browse(cr, uid, ids):
            if retro.state == 'done'\
                    and retro.amount_paid == 0\
                    and not retro.is_regulation:
                return False

        return True

    _constraints = [
        (_check_unicity,
         _("A retrocession already exists for this mandate at this period"),
         ['sta_mandate_id',
          'ext_mandate_id']),
        (_check_value,
         _("You can not validate a negative retrocession"),
         ['amount_total']),
        (_check_regulation,
         _("A regulation retrocession should only occur on December"),
         ['is_regulation']),
        (_check_paid,
         _("No amount paid specified."),
         ['state'])]

    _unicity_keys = 'N/A'

# orm methods

    def create(self, cr, uid, vals, context=None):
        if vals.get('sta_mandate_id', False):
            vals['mandate_ref'] = "sta.mandate,%s" % vals.get('sta_mandate_id')
        else:
            vals['mandate_ref'] = "ext.mandate,%s" % vals.get('ext_mandate_id')
        if vals.get('month', '') != '12':
            vals['is_regulation'] = False
        res = super(retrocession, self).create(cr, uid, vals, context=context)
        if res:
            retro = self.browse(cr, uid, res, context=context)
            if not retro.is_regulation:
                if retro.mandate_ref.calculation_method_id:
                    model = self.pool['calculation.method']
                    model.copy_variable_rules_on_retrocession(
                        cr,
                        uid,
                        retro.mandate_ref.calculation_method_id.id,
                        retro.id,
                        context=context)

                for rule in retro.mandate_ref.rule_ids:
                    data = self.pool['calculation.rule'].get_copy_fields_value(
                        cr,
                        uid,
                        rule)
                    data['retrocession_id'] = retro.id
                    self.pool['calculation.rule'].create(
                        cr,
                        uid,
                        data,
                        context=context)

                for rule in retro.mandate_ref.deductible_rule_ids:
                    data = self.pool['calculation.rule'].get_copy_fields_value(
                        cr,
                        uid,
                        rule)
                    data['retrocession_id'] = retro.id
                    self.pool['calculation.rule'].create(
                        cr,
                        uid,
                        data,
                        context=context)

        return res

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []
        for retro in self.browse(cr, uid, ids, context=context):
            mandate_name = self.pool.get(
                retro.mandate_ref._name).name_get(
                cr,
                uid,
                retro.mandate_ref.id,
                context=context)

            if retro.month:
                fields = self.fields_get(cr, uid, ['month'], context=context)
                interval_type_selection = dict(fields['month']['selection'])

                display_month = interval_type_selection.get(retro.month)
                display_name = u'{mandate} ({month} {year})'.format(
                    month=display_month,
                    year=retro.year,
                    mandate=mandate_name[0][1])
            else:
                display_name = u'{mandate} ({year})'.format(
                    year=retro.year,
                    mandate=mandate_name[0][1])

            res.append((retro['id'], display_name))
        return res

# view methods: onchange, button

    def onchange_sta_mandate_id(
            self,
            cr,
            uid,
            ids,
            sta_mandate_id,
            context=None):
        res = {}
        if sta_mandate_id:
            retrocession_mode = self.pool.get('sta.mandate').read(
                cr,
                uid,
                sta_mandate_id,
                ['retrocession_mode'],
                context=context)['retrocession_mode']
            res['value'] = dict(retrocession_mode=retrocession_mode or False)

        return res

    def onchange_ext_mandate_id(
            self,
            cr,
            uid,
            ids,
            ext_mandate_id,
            context=None):
        res = {}
        if ext_mandate_id:
            retrocession_mode = self.pool.get('ext.mandate').read(
                cr,
                uid,
                ext_mandate_id,
                ['retrocession_mode'],
                context=context)['retrocession_mode']
            res['value'] = dict(retrocession_mode=retrocession_mode or False)

        return res

    def button_dummy(self, cr, uid, retro_id, context=None):
        return True

    def action_validate(self, cr, uid, ids, context=None):
        """
        =================
        action_validate
        =================
        Change state of retrocession to 'Validated' and generate account move
        if needed
        :rparam: False
        :rtype: Boolean
        """
        # copy fixed rules on retrocession to keep history of calculation basis
        for retrocession in self.browse(cr, uid, ids, context=context):
            if retrocession.amount_total < 0 and \
                    not retrocession.is_regulation:
                raise except_orm(
                    _('Error'),
                    _('Amount due for retrocession should be positive'))
            self.write(
                cr, uid, retrocession.id, {
                    'state': 'validated'}, context=context)
            if not retrocession.unique_id:
                retro_number = '{mandate}/{year}{month}{regulation}'.format(
                    mandate=retrocession.mandate_ref.unique_id,
                    year=retrocession.year,
                    month=str(
                        retrocession.month).rjust(
                        2,
                        '0') if retrocession.month else "00",
                    regulation='1' if retrocession.is_regulation else '0')
                self.write(
                    cr, uid, retrocession.id, {
                        'unique_id': retro_number}, context=context)
                retrocession = self.browse(
                    cr,
                    uid,
                    retrocession.id,
                    context=context)

            if retrocession.need_account_management:
                self.generate_account_move(cr, uid, retrocession, context)

            if retrocession.amount_total == 0:
                self.action_done(cr, uid, [retrocession.id], context=context)
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
        account_move_ids = [
            retro_data['move_id'][0] for retro_data in self.read(
                cr,
                uid,
                ids,
                ['move_id'],
                context=context) if retro_data['move_id']]
        self.pool.get('account.move').button_cancel(
            cr,
            uid,
            account_move_ids,
            context=context)
        self.pool.get('account.move').unlink(
            cr,
            uid,
            account_move_ids,
            context=context)
        return super(
            retrocession,
            self).action_invalidate(
            cr,
            uid,
            ids,
            context=context,
            vals=vals)

    def action_revalidate(self, cr, uid, ids, context=None, vals=None):
        """
        =================
        action_revalidate
        =================
        Reset Retrocession to draft state unlinking generated fixed rules
        """
        vals = vals or {}
        vals.update({'state': 'draft'})
        res = super(
            retrocession,
            self).action_revalidate(
            cr,
            uid,
            ids,
            context=context,
            vals=vals)
        account_move_ids = [
            retro_data['move_id'][0] for retro_data in self.read(
                cr,
                uid,
                ids,
                ['move_id'],
                context=context) if retro_data['move_id']]
        self.pool.get('account.move').button_cancel(
            cr,
            uid,
            account_move_ids,
            context=context)
        self.pool.get('account.move').unlink(
            cr,
            uid,
            account_move_ids,
            context=context)
        return res

    def action_done(self, cr, uid, ids, context=None):
        """
        =================
        action_done
        =================
        Mark a retrocession as done
        """
        return super(
            retrocession,
            self).action_invalidate(
            cr,
            uid,
            ids,
            context=context,
            vals={
                'provision': 0.0,
                'state': 'done'})

    def action_request_for_payment_send(self, cr, uid, ids, context=None):
        """
        Send an email with request for payment attached
        """
        tmpl_xmlid = 'email_template_request_payment_retrocession'
        ir_model_data = self.pool.get('ir.model.data')
        retro = self.browse(cr, uid, ids[0], context=context)
        if not retro.email_coordinate_id:
            raise orm.except_orm(
                _('Error'),
                _('Representative has no email specified'))
        try:
            template_id = ir_model_data.get_object_reference(
                cr, uid, 'mozaik_retrocession', tmpl_xmlid)[1]
        except ValueError:
            raise orm.except_orm(
                _('Error'),
                _('Email template %s not found!') % tmpl_xmlid)

        if template_id:
            # Remove navigation history: maybe we're coming from a mandate
            ctx = dict(context or {})
            ctx.pop('active_model', None)
            ctx.pop('active_id', None)
            ctx.pop('active_ids', None)
            composer = self.pool['mail.compose.message']
            mail_composer_vals = {'parent_id': False,
                                  'use_active_domain': False,
                                  'partner_ids': [[6, False,
                                                   [retro.partner_id.id]]],
                                  'notify': False,
                                  'template_id': template_id,
                                  'model': self._name,
                                  'record_name': retro.display_name,
                                  'res_id': retro.id,
                                  }
            value = composer.onchange_template_id(
                cr, uid, False, template_id, False,
                False, retro.id,
                context=ctx)['value']
            if value.get('attachment_ids'):
                value['attachment_ids'] = [
                    [6, False, value['attachment_ids']]
                ]
            value['email_from'] = composer._get_default_from(
                cr, uid, context=ctx)
            mail_composer_vals.update(value)
            mail_composer_id = composer.create(
                cr, uid, mail_composer_vals, context=ctx)
            composer.send_mail(cr, uid, [mail_composer_id], context=ctx)
            self.write(cr, uid, retro.id,
                       {'email_date': fields.date.today()}, context=ctx)

    def generate_account_move(self, cr, uid, retro, context=None):
        """
        Generate account move for retrocession(s)
        :rparam: None
        :rtype: None
        """
        retro_journal_ids = self.pool.get('account.journal').search(
            cr, uid, [
                ('code', '=', 'RETRO')], context=context)
        if not retro_journal_ids:
            retro_journal_ids = self.pool.get('account.journal').search(
                cr, uid, [
                    ('type', '=', 'sale')], context=context)

        retro_journal_id = retro_journal_ids[0]
        retro_journal = self.pool.get('account.journal').browse(
            cr,
            uid,
            retro_journal_id,
            context=context)
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')

        month = retro.month if retro.month else 12

        date_str = '{day}{month}{year}'.format(
            day=31 if month == '12' else '01',
            month=month,
            year=retro.year)
        date_account_move = datetime.strptime(date_str, '%d%m%Y')

        move_vals = move_obj.account_move_prepare(
            cr,
            uid,
            retro_journal.id,
            date=date_account_move,
            ref=retro.mandate_ref.reference,
            context=context)
        move_id = move_obj.create(cr, uid, move_vals, context=context)

        line_vals = dict(name=retro.unique_id,
                         partner_id=retro.partner_id.id,
                         account_id=False,
                         debit=0,
                         credit=0,
                         move_id=move_id)

        deduc_rules_amount = sum(rule['amount_subtotal'] * -1
                                 for rule in retro.deductible_rule_ids)

        column1 = 'credit'
        column2 = 'debit'
        amount_total = retro.amount_total
        if retro.amount_total < 0:
            column1 = 'debit'
            column2 = 'credit'
            amount_total *= -1

        line_vals[column1] = (amount_total + deduc_rules_amount)
        line_vals[column2] = 0
        if retro.default_credit_account:
            line_vals['account_id'] = retro.default_credit_account.id
        else:
            raise orm.except_orm(
                _('Error'),
                _('Please set a retrocession account on mandate category.'))
        move_line_obj.create(cr, uid, line_vals)

        if deduc_rules_amount > 0:
            line_vals[column1] = 0
            line_vals[column2] = deduc_rules_amount
            if retro.default_debit_account:
                line_vals['account_id'] = retro.default_debit_account.id
            else:
                raise orm.except_orm(
                    _('Error'),
                    _('Please set a cost account on mandate category.'))
            move_line_obj.create(cr, uid, line_vals)

        if amount_total != 0:
            line_vals[column1] = 0
            line_vals[column2] = amount_total
            line_vals['account_id'] = retro_journal.default_debit_account_id.id
            move_line_obj.create(cr, uid, line_vals)

        self.write(cr, uid, retro.id, {'move_id': move_id}, context=context)
        move_obj.post(cr, uid, [move_id], context=context)
