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
from datetime import datetime
from dateutil.relativedelta import relativedelta

WIZARD_AVAILABLE_ACTIONS = [
    ('renew', 'Renew Mandate'),
    ('add', 'Add Complementary Mandate'),
]


class abstract_copy_mandate_wizard(orm.AbstractModel):
    _name = 'abstract.copy.mandate.wizard'

    _form_view = 'abstract_mandate_form_view'
    _mandate_assembly_foreign_key = False

    _columns = {
        'mandate_category_id': fields.many2one(
            'mandate.category', string='Mandate Category', ondelete='cascade'),
        'new_mandate_category_id': fields.many2one(
            'mandate.category', string='Mandate Category', ondelete='cascade'),
        'mandate_id': fields.many2one(
            'abstract.mandate', string='Abstract Mandate',
            readonly=True, ondelete='cascade'),
        'assembly_id': fields.many2one(
            'abstract.assembly', string='Abstract Assembly',
            readonly=True, ondelete='cascade'),
        'new_assembly_id': fields.many2one(
            'abstract.assembly', string='Abstract Assembly', ondelete='cascade'),
        'instance_id': fields.many2one(
            'abstract.instance', string='Abstract Instance', ondelete='cascade'),
        'action': fields.selection(WIZARD_AVAILABLE_ACTIONS, 'Action'),
        'partner_id': fields.many2one(
            'res.partner', string='Partner',
            readonly=True, ondelete='cascade'),
        'start_date': fields.date('Start Date'),
        'deadline_date': fields.date('Deadline Date'),
        'message': fields.char('Message', size=250),
    }

# constraints

    _sql_constraints = [
        ('date_check', "CHECK(start_date <= deadline_date)",
         "The start date must be anterior to the deadline date."),
    ]

# orm methods

    def default_get(self, cr, uid, flds, context):
        """
        To get default values for the object.
        """
        res = {}
        context = context or {}

        model = context.get('active_model', False)
        if not model:
            return res

        ids = context.get('active_ids') \
            or (context.get('active_id') and [context.get('active_id')]) \
            or []

        for mandate in self.pool[model].browse(cr, uid, ids, context=context):
            action = False

            limit_date = mandate.end_date or mandate.deadline_date

            if limit_date > fields.datetime.now():
                action = WIZARD_AVAILABLE_ACTIONS[1][0]
            else:
                action = WIZARD_AVAILABLE_ACTIONS[0][0]

            res['partner_id'] = mandate.partner_id.id
            res['mandate_category_id'] = mandate.mandate_category_id.id
            res['assembly_id'] = res['new_assembly_id']\
                               = mandate[self._mandate_assembly_foreign_key].id
            res['mandate_id'] = mandate.id
            res['instance_id'] =\
                     mandate[self._mandate_assembly_foreign_key].instance_id.id
            if action == 'add':
                res['start_date'] = mandate.start_date
                res['deadline_date'] = mandate.deadline_date
            if action == 'renew':
                start_date = mandate.end_date if mandate.end_date\
                                              else mandate.deadline_date
                start_date = (datetime.strptime(start_date,
                                                '%Y-%m-%d') +\
                              relativedelta(days=1))
                res['start_date'] = start_date.strftime('%Y-%m-%d')
            res['action'] = action
            break

        return res

# view methods: onchange, button

    def renew_mandate(self, cr, uid, ids, vals, context=None):
        """
        ====================
        renew_mandate
        ====================
        Renew a mandate
        """
        wizard = self.browse(cr, uid, ids, context=context)[0]
        vals['start_date'] = wizard.start_date,
        vals['deadline_date'] = wizard.deadline_date,
        vals['end_date'] = False
        return self.copy_mandate(cr, uid, wizard.mandate_id.id, vals,
                                 context=context)

    def add_mandate(self, cr, uid, ids, context=None):
        """
        ===========
        add_mandate
        ===========
        Add a complementary mandate
        """
        wizard = self.browse(cr, uid, ids, context=context)[0]
        values = dict(mandate_category_id=wizard.new_mandate_category_id.id,
                      start_date=wizard.start_date,
                      deadline_date=wizard.deadline_date,
                      candidature_id=False)

        values[self._mandate_assembly_foreign_key] = wizard.new_assembly_id.id
        return self.copy_mandate(cr, uid, wizard.mandate_id.id, values,
                                 context=context)

# public methods

    def copy_mandate(self, cr, uid, mandate_id, vals, context=None):
        """
        ===========
        copy_mandate
        ===========
        Copy a mandate with new default values
        """
        mandate_obj = self.pool[context.get('active_model')]

        res = dict(type='ir.actions.act_window',
                   view_type='form',
                   view_mode='form',
                   target='current',
                   nodestroy=True,
                   res_model=context.get('active_model'),
                   name=_(mandate_obj._description),)

        new_mandate_id = mandate_obj.copy(cr, uid, mandate_id, default=vals,
                                          context=context)
        view_ref = self.pool.get('ir.model.data').get_object_reference(
                                                               cr,
                                                               uid,
                                                               'mozaik_mandate',
                                                               self._form_view)
        view_id = view_ref and view_ref[1] or False,

        res['res_id'] = new_mandate_id
        res['view_id'] = view_id

        return res


class copy_sta_mandate_wizard(orm.TransientModel):
    _name = "copy.sta.mandate.wizard"
    _inherit = ['abstract.copy.mandate.wizard']

    _form_view = 'sta_mandate_form_view'
    _mandate_assembly_foreign_key = 'sta_assembly_id'

    _columns = {
        'mandate_id': fields.many2one(
            'sta.mandate', string='State Mandate',
            readonly=True, ondelete='cascade'),
        'assembly_id': fields.many2one(
            'sta.assembly', string='State Assembly',
            readonly=True, ondelete='cascade'),
        'new_assembly_id': fields.many2one(
            'sta.assembly', string='State Assembly', ondelete='cascade'),
        'instance_id': fields.many2one(
            'sta.instance', string='State Instance', ondelete='cascade'),
        'is_legislative': fields.boolean('Is Legislative'),
        'legislature_id': fields.many2one(
            'legislature', string='Legislature', ondelete='cascade'),
    }

    _defaults = {
        'is_legislative': False
    }

    def default_get(self, cr, uid, flds, context):
        """
        To get default values for the object.
        """
        res = super(copy_sta_mandate_wizard, self).default_get(cr,
                                                               uid,
                                                               flds,
                                                               context=context)

        ids = context.get('active_id') and\
              [context.get('active_id')] or context.get('active_ids') or []
        model = context.get('active_model', False)
        if not model:
            return res

        for mandate in self.pool[model].browse(cr, uid, ids, context=context):
            domain = [
              ('power_level_id', '=',
               mandate.sta_assembly_id.assembly_category_id.power_level_id.id),
            ('start_date', '>', fields.datetime.now())]
            legislature_ids = self.pool['legislature'].search(cr, uid, domain)
            legislature_id = False
            if legislature_ids:
                legislature_id = legislature_ids[0]

            if mandate.sta_assembly_id.is_legislative and\
               res['action'] == WIZARD_AVAILABLE_ACTIONS[0][0]:
                res['message'] = \
                                _('Renew not allowed on a legislative mandate')

            res['legislature_id'] = legislature_id
            res['is_legislative'] = mandate.sta_assembly_id.is_legislative
            if res['is_legislative']:
                res.pop('new_assembly_id', False)

            break

        return res

    def onchange_legislature_id(self, cr, uid, ids, legislature_id,
                                context=None):
        res = {}
        res['value'] = dict(mandate_start_date=False,
                            mandate_deadline_date=False)
        if legislature_id:
            legislature_data = self.pool.get('legislature').read(
                                                             cr,
                                                             uid,
                                                             legislature_id,
                                                             ['start_date',
                                                              'deadline_date'])
            res['value'] = dict(start_date=legislature_data['start_date'],
                            deadline_date=legislature_data['deadline_date'])
        return res

    def renew_mandate(self, cr, uid, ids, context=None):
        """
        ====================
        renew_mandate
        ====================
        Renew a mandate
        """
        wizard = self.browse(cr, uid, ids, context=context)[0]
        values = dict(legislature_id=wizard.legislature_id.id)
        return super(copy_sta_mandate_wizard, self).renew_mandate(
                                                              cr,
                                                              uid,
                                                              ids,
                                                              values,
                                                              context=context)

    def add_mandate(self, cr, uid, ids, context=None):
        """
        ===========
        add_mandate
        ===========
        Add a complementary mandate
        """
        return super(copy_sta_mandate_wizard, self).add_mandate(
                                                            cr,
                                                            uid,
                                                            ids,
                                                            context=context)


class copy_int_mandate_wizard(orm.TransientModel):
    _name = "copy.int.mandate.wizard"
    _inherit = ['abstract.copy.mandate.wizard']

    _form_view = 'int_mandate_form_view'
    _mandate_assembly_foreign_key = 'int_assembly_id'

    _columns = {
        'mandate_id': fields.many2one(
            'int.mandate', string='Internal Mandate',
            readonly=True, ondelete='cascade'),
        'assembly_id': fields.many2one(
            'int.assembly', string='Internal Assembly',
            readonly=True, ondelete='cascade'),
        'new_assembly_id': fields.many2one(
            'int.assembly', string='Internal Assembly', ondelete='cascade'),
        'instance_id': fields.many2one(
            'int.instance', string='Internal Instance', ondelete='cascade'),
    }

    def default_get(self, cr, uid, flds, context):
        """
        To get default values for the object.
        """
        return super(copy_int_mandate_wizard, self).default_get(
                                                            cr,
                                                            uid,
                                                            flds,
                                                            context=context)

    def renew_mandate(self, cr, uid, ids, context=None):
        """
        ====================
        renew_mandate
        ====================
        Renew a mandate
        """
        return super(copy_int_mandate_wizard, self).renew_mandate(
                                                              cr,
                                                              uid,
                                                              ids,
                                                              {},
                                                              context=context)

    def add_mandate(self, cr, uid, ids, context=None):
        """
        ===========
        add_mandate
        ===========
        Add a complementary mandate
        """
        return super(copy_int_mandate_wizard, self).add_mandate(
                                                            cr,
                                                            uid,
                                                            ids,
                                                            context=context)


class copy_ext_mandate_wizard(orm.TransientModel):
    _name = "copy.ext.mandate.wizard"
    _inherit = ['abstract.copy.mandate.wizard']

    _form_view = 'ext_mandate_form_view'
    _mandate_assembly_foreign_key = 'ext_assembly_id'

    _columns = {
        'mandate_id': fields.many2one(
            'ext.mandate', string='External Mandate',
            readonly=True, ondelete='cascade'),
        'assembly_id': fields.many2one(
            'ext.assembly', string='External Assembly',
            readonly=True, ondelete='cascade'),
        'new_assembly_id': fields.many2one(
            'ext.assembly', string='External Assembly', ondelete='cascade'),
        'instance_id': fields.many2one(
            'int.instance', string='Internal Instance', ondelete='cascade'),
    }

    def default_get(self, cr, uid, flds, context):
        """
        To get default values for the object.
        """
        return super(copy_ext_mandate_wizard, self).default_get(
                                                            cr,
                                                            uid,
                                                            flds,
                                                            context=context)

    def renew_mandate(self, cr, uid, ids, context=None):
        """
        ====================
        renew_mandate
        ====================
        Renew a mandate
        """
        return super(copy_ext_mandate_wizard, self).renew_mandate(
                                                              cr,
                                                              uid,
                                                              ids,
                                                              {},
                                                              context=context)

    def add_mandate(self, cr, uid, ids, context=None):
        """
        ===========
        add_mandate
        ===========
        Add a complementary mandate
        """
        return super(copy_ext_mandate_wizard, self).add_mandate(
                                                            cr,
                                                            uid,
                                                            ids,
                                                            context=context)
