# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrModel(models.Model):

    _inherit = 'ir.model'

    @api.model
    def _get_active_relations(self, objects, with_ids=False):
        self = self.sudo()  # TODO

        # force active_test in context to be sure to not retrieve inactive
        # documents later in this method
        # TODO ir.model.fields doesn't have a active field, so I set the
        # TODO context here to profit of it in the for loop below, but it need
        # TODO to be verified
        # TODO ctx was previously used for active_dep_ids = model.search(
        imf_obj = self.env['ir.model.fields'].with_context(active_test=True)

        relations = imf_obj.search(
            [('relation', '=', objects._name), ('ttype', '=', 'many2one')])

        results = {}
        for record in objects:
            relation_models = {}
            for relation in relations:
                model = relation.model_id
                if not model:
                    continue
                if not model._auto or model._transient:
                    continue
                if not model._fields.get(relation.name):
                    continue
                if not model._fields.get('active'):
                    continue

                col = model._fields[relation.name]
                if hasattr(col, 'store') and not col.store:
                    continue
                if hasattr(model, '_allowed_inactive_link_models'):
                    if record._name in model._allowed_inactive_link_models:
                        continue

                active_dep_ids = model.search(
                    [(relation.name, '=', record.id)])

                if active_dep_ids:
                    if with_ids:
                        relation_models.update({
                            relation.model: active_dep_ids
                        })
                        results.update({record.id: relation_models})
                    else:
                        results.update({record.id: relation.model})

        return results

    @api.model
    def _get_relation_column_name(self, model_name, relation_model_name):
        relations = self.env['ir.model.fields'].search(
            [('model', '=', model_name),
             ('relation', '=', relation_model_name),
             ('ttype', '=', 'many2one')])
        if relations:
            return relations[0].name

        return False
