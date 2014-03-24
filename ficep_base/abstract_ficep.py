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

INVALIDATE_ERROR = _('Invalidation impossible, at least one dependency is still active')


class abstract_ficep_model (orm.AbstractModel):
    _name = "abstract.ficep.model"
    _description = "Abstract Ficep Model"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _check_invalidate(self, cr, uid, ids, for_unlink=False, context=None):
        """
        ==========================
        _check_invalidate
        ==========================
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
        'create_date': fields.datetime('Creation Date', readonly=True),
        'expire_date': fields.datetime('Expiration Date', track_visibility='onchange'),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True,
    }

    _constraints = [
        (_check_invalidate, INVALIDATE_ERROR, ['expire_date'])
    ]
