# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, tools
from odoo.fields import first


class IrModel(models.Model):
    _inherit = "ir.model"

    @api.model
    def _get_active_relations(self, objects, with_ids=False):
        self = self.sudo()
        imf_obj = self.env["ir.model.fields"]
        model_name = first(objects)._name
        relations = imf_obj.search(
            [
                ("relation", "=", model_name),
                ("ttype", "=", "many2one"),
            ]
        )

        results = {}
        for record in objects:
            relation_models = {}
            for relation in relations:
                model_obj = self.env.get(relation.model_id.model)
                if not isinstance(model_obj, models.BaseModel):
                    continue
                if not tools.table_exists(self.env.cr, model_obj._table):
                    continue
                if not model_obj._auto or model_obj._transient:
                    continue
                if not model_obj._fields.get(relation.name):
                    continue
                if not model_obj._fields.get("active"):
                    continue

                field = model_obj._fields.get(relation.name)
                if field.compute:
                    continue
                if hasattr(model_obj, "_allowed_inactive_link_models"):
                    if record._name in model_obj._allowed_inactive_link_models:
                        continue

                domain = [
                    (relation.name, "=", record.id),
                ]
                # In case of the relation is the same model than given object,
                # we have to add a domain to avoid infinite loop
                if model_obj._name == model_name:
                    domain.append(("id", "not in", objects.ids))
                active_dep_ids = model_obj.with_context(active_test=True).search(domain)

                if active_dep_ids:
                    if with_ids:
                        relation_models.update(
                            {
                                relation.model: active_dep_ids,
                            }
                        )
                        results.update({record.id: relation_models})
                    else:
                        results.update({record.id: relation.model})

        return results

    @api.model
    def _get_relation_column_name(self, model_name, relation_model_name):
        relation = self.env["ir.model.fields"].search(
            [
                ("model", "=", model_name),
                ("relation", "=", relation_model_name),
                ("ttype", "=", "many2one"),
            ],
            limit=1,
        )
        return relation.name
