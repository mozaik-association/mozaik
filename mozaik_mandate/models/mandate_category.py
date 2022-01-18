# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

# Constants
MANDATE_CATEGORY_AVAILABLE_TYPES = [
    ("sta", "State"),
    ("int", "Internal"),
    ("ext", "External"),
]

mandate_category_available_types = dict(MANDATE_CATEGORY_AVAILABLE_TYPES)


class MandateCategory(models.Model):
    _name = "mandate.category"
    _description = "Mandate Category"
    _inherit = ["mozaik.abstract.model"]
    _order = "name"

    _unicity_keys = "type, assembly_categoryid, name"

    _sql_constraints = [
        (
            "ref_categ_check",
            "CHECK("
            "(sta_assembly_category_id>0 and "
            " int_assembly_category_id is null and "
            " ext_assembly_category_id is null)"
            " OR "
            "(int_assembly_category_id>0 and "
            " sta_assembly_category_id is null and "
            " ext_assembly_category_id is null)"
            " OR "
            "(ext_assembly_category_id>0 and "
            " int_assembly_category_id is null and "
            " sta_assembly_category_id is null)"
            ")",
            "An Assembly Category is required.",
        ),
    ]

    name = fields.Char(required=True, index=True, tracking=True)
    type = fields.Selection(
        selection=MANDATE_CATEGORY_AVAILABLE_TYPES, index=True, required=True
    )
    sta_assembly_category_id = fields.Many2one(
        comodel_name="sta.assembly.category",
        string="State Assembly Category",
        tracking=True,
    )
    ext_assembly_category_id = fields.Many2one(
        comodel_name="ext.assembly.category",
        string="External Assembly Category",
        tracking=True,
    )
    int_assembly_category_id = fields.Many2one(
        comodel_name="int.assembly.category",
        string="Internal Assembly Category",
        tracking=True,
    )
    assembly_categoryid = fields.Integer(
        string="Assembly category",
        compute="_compute_assembly_categoryid",
        store=True,
        required=True,
        # to avoid null for required=True
        default=0,
    )
    sta_mandate_ids = fields.One2many(
        comodel_name="sta.mandate",
        inverse_name="mandate_category_id",
        string="State Mandates",
    )
    int_mandate_ids = fields.One2many(
        comodel_name="int.mandate",
        inverse_name="mandate_category_id",
        string="Internal Mandates",
    )
    ext_mandate_ids = fields.One2many(
        comodel_name="ext.mandate",
        inverse_name="mandate_category_id",
        string="External Mandates",
    )
    with_revenue_declaration = fields.Boolean(
        help="Representative is subject to a declaration of income"
    )
    with_assets_declaration = fields.Boolean(
        help="Representative is subject to a declaration of assets"
    )
    with_remuneration = fields.Boolean(
        default=lambda s: s._default_with_remuneration(),
    )
    int_power_level_id = fields.Many2one(
        "int.power.level",
        string="Internal Power Level",
        related="int_assembly_category_id.power_level_id",
        store=True,
    )
    sta_power_level_id = fields.Many2one(
        "sta.power.level",
        string="State Power Level",
        related="sta_assembly_category_id.power_level_id",
        store=True,
    )

    @api.depends(
        "sta_assembly_category_id",
        "int_assembly_category_id",
        "ext_assembly_category_id",
    )
    def _compute_assembly_categoryid(self):
        """
        Compute pseudo assembly category m2o for unicity key
        """
        for record in self:
            record.assembly_categoryid = (
                record.sta_assembly_category_id.id
                or record.int_assembly_category_id.id
                or record.ext_assembly_category_id.id
                or 0
            )

    @api.model
    def _default_with_remuneration(self):
        res = False
        if self.env.context.get("default_type", "") == "sta":
            res = True
        return res

    def copy_data(self, default=None):
        res = super().copy_data(default=default)

        res[0].update(
            {
                "name": _("%s (copy)") % res[0].get("name"),
            }
        )
        return res
