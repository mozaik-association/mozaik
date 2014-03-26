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
import logging
from lxml import etree

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import SUPERUSER_ID

_logger = logging.getLogger(__name__)


INVALIDATE_ERROR = _('Invalidation impossible, at least one dependency is still active')


class abstract_ficep_model (orm.AbstractModel):
    _name = "abstract.ficep.model"
    _description = "Abstract Ficep Model"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def action_invalidate(self, cr, uid, ids, context=None):
        """
        =================
        action_invalidate
        =================
        Invalidates an object by setting
        * active to False
        * expire_date to current date
        :rparam: True
        :rtype: boolean

        """
        vals = self.get_fields_to_update(cr, uid, 'deactivate', context=context)
        return self.write(cr, uid, ids, vals, context=context)

    def action_validate(self, cr, uid, ids, context=None):
        """
        =================
        action_validate
        =================
        Validates an object by setting
        * active to True
        * expire_date to False
        :rparam: True
        :rtype: boolean

        """
        vals = self.get_fields_to_update(cr, uid, 'activate', context=context)
        return self.write(cr, uid, ids, vals, context=context)

    def get_fields_to_update(self, cr, uid, mode, context=None):
        """
        ====================
        get_fields_to_update
        ====================
        :param mode: return a dictionary depending on mode value
        :type mode: char
        """

        if mode == 'deactivate':
            return {'active': False,
                    'expire_date': fields.datetime.now(),
                   }
        elif mode == 'activate':
            return {'active': True,
                    'expire_date': False,
                   }
        else:
            return {}

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'expire_date': fields.datetime('Expiration Date', track_visibility='onchange'),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True,
    }

# constraints

    def _check_invalidate(self, cr, uid, ids, for_unlink=False, context=None):
        """
        =================
        _check_invalidate
        =================
        Check if object can be desactivated, dependencies must be desactivated before
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        invalidate_ids = list(ids)
        ficep_models = self.browse(cr, uid, invalidate_ids)
        for ficep_model in ficep_models:
            if not ficep_model.expire_date:
                invalidate_ids.remove(ficep_model.id)

        if invalidate_ids:
            rels_dict = self.pool.get('ir.model')._get_active_relations(cr, uid, invalidate_ids, self._name, context=context)

            if len(rels_dict) > 0:
                return False

        return True

    _constraints = [
        (_check_invalidate, INVALIDATE_ERROR, ['expire_date'])
    ]

# orm methods

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if view_type == 'form' and uid != SUPERUSER_ID and not context.get('is_developper'):
            context = dict(context or {}, add_readonly_condition=True) 
        res = super(abstract_ficep_model, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        return res

# Replace the orm.transfer_node_to_modifiers functions.

original_transfer_node_to_modifiers = orm.transfer_node_to_modifiers

def transfer_node_to_modifiers(node, modifiers, context=None, in_tree_view=False):
    '''
    Add conditions on usefull fields (but chatting fields) to make readonly the form if the document is inactive
    '''
    fct_src = original_transfer_node_to_modifiers
    trace = True
    
    if context and context.get('add_readonly_condition'):
        context.pop('add_readonly_condition')

        if trace:
            # etree.tostring(node)
            pass
        if node.xpath("//field[@name='active'][not(ancestor::field)]"):
            for nd in node.xpath("//field[not(ancestor::div[(@name='dev') or (@name='chat')])][not(ancestor::field)]"):
                attrs_str = nd.get('attrs') or '{}'
                before = after = eval(attrs_str)
                if after.get('readonly'):
                    dom = after.get('readonly')[1:-1]
                    if len(dom.split("'active'")) > 1:
                        continue
                    else:
                        dom = ['|', ('active', '=', False), dom]
                        after['readonly'] = dom
                else:
                    after['readonly'] = [('active', '=', False)]
                after = str(after)
                nd.set('attrs', after)
                if trace:
                    _logger.info('Field %s - attrs before: %s - after: %s', nd.get('name'), str(before), after)

    return fct_src(node, modifiers, context=context, in_tree_view=in_tree_view)

orm.transfer_node_to_modifiers = transfer_node_to_modifiers

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
