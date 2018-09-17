# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartnerRelationAll(models.AbstractModel):

    _inherit = 'res.partner.relation.all'

    this_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string='This Internal Instance', readonly=True)
    other_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string='Other Internal Instance', readonly=True)

    # @api.model
    # def _get_additional_relation_columns(self):
    #     res = super()._get_additional_relation_columns()
        # added_fields = ', rel.left_instance_id' \
        #                ', rel.right_instance_id'
        # return "%s%s" % (res, added_fields)

    # @api.model
    # def _get_additional_view_fields(self):
    #     res = super()._get_additional_view_fields()
    #     added_fields = (
    #         ", "
    #         "CASE"
    #         "   WHEN NOT bas.is_inverse"
    #         "   THEN bas.left_instance_id"
    #         "   ELSE bas.right_instance_id "
    #         "END as this_instance_id, "
    #         "CASE"
    #         "   WHEN NOT bas.is_inverse"
    #         "   THEN bas.right_instance_id"
    #         "   ELSE bas.left_instance_id "
    #         "END as other_instance_id")
    #     return "%s%s" % (res, added_fields)
