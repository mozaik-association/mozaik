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
from openerp.tools import SUPERUSER_ID


class ir_model(orm.Model):

    _inherit = 'ir.model'

    def _get_active_relations(self, cr, uid, ids, model_name, context=None):
        uid = SUPERUSER_ID
        relation_ids = self.pool.get('ir.model.fields').search(cr, uid, [('relation', '=', model_name),
                                                                         ('ttype', '=', 'many2one')],
                                                               context=context)
        relations = self.pool.get('ir.model.fields').browse(cr, uid, relation_ids, context=context)

        results = {}
        for record_id in ids:
            for relation in relations:
                model = self.pool.get(relation.model, False)
                if model._transient:
                    continue
                if not model or not model._auto or not model._columns.get(relation.name):
                    continue
                col = model._columns[relation.name]
                if hasattr(col, 'store') and not col.store:
                    continue
                if hasattr(model, '_allowed_inactive_link_models'):
                    if model_name in model._allowed_inactive_link_models:
                        continue

                active_dep_ids = model.search(cr, uid, [(relation.name, '=', record_id)], context=context)

                if len(active_dep_ids) > 0:
                    results.update({record_id: relation.model})

        return results


class ir_model_data(orm.Model):

    _inherit = 'ir.model.data'

# public methods

    def get_object_alternative(self, cr, uid, module, xml_id, alt_module, alt_xml_id):
        """
        Returns (model, res_id) corresponding to the given (module, xml_id) couple or, if not found,
        to the alternative given couple
        """
        try:
            return self.get_object_reference(cr, uid, module, xml_id)
        except ValueError:
            pass
        except:
            raise

        return self.get_object_reference(cr, uid, alt_module, alt_xml_id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
