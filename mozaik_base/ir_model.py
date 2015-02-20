# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_base, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_base is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_base is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_base.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp.tools import SUPERUSER_ID


class ir_model(orm.Model):

    _inherit = 'ir.model'

    def _get_active_relations(
            self, cr, uid, ids, model_name, context=None, with_ids=False):
        uid = SUPERUSER_ID
        imf_obj = self.pool['ir.model.fields']
        relation_ids = imf_obj.search(
            cr, uid,
            [('relation', '=', model_name), ('ttype', '=', 'many2one')],
            context=context)
        relations = imf_obj.browse(cr, uid, relation_ids, context=context)

        # force active_test in context to be sure to not retrieve inactive
        # documents later in this method
        ctx = dict(context or {}, active_test=True)

        results = {}
        for record_id in ids:
            relation_models = {}
            for relation in relations:
                model = self.pool.get(relation.model, False)
                if not model:
                    continue
                if not model._auto or model._transient:
                    continue
                if not model._columns.get(relation.name):
                    continue

                col = model._columns[relation.name]
                if hasattr(col, 'store') and not col.store:
                    continue
                if hasattr(model, '_allowed_inactive_link_models'):
                    if model_name in model._allowed_inactive_link_models:
                        continue

                active_dep_ids = model.search(
                    cr, uid, [(relation.name, '=', record_id)], context=ctx)

                if len(active_dep_ids) > 0:
                    if with_ids:
                        relation_models.update({
                            relation.model: active_dep_ids
                        })
                        results.update({record_id: relation_models})
                    else:
                        results.update({record_id: relation.model})

        return results

    def _get_relation_column_name(self, cr, uid, model_name, relation_model_name, context=None):
        relation_ids = self.pool.get('ir.model.fields').search_read(cr, uid, [('model', '=', model_name),
                                                                              ('relation', '=', relation_model_name),
                                                                              ('ttype', '=', 'many2one')],
                                                                              fields=['name'], context=context)
        if relation_ids:
            return relation_ids[0]['name']

        return False
