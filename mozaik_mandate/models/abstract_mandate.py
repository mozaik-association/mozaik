# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AbstractMandate(models.AbstractModel):
    _name = "abstract.mandate"
    _description = "Abstract Mandate"
    _inherit = ["mozaik.abstract.model"]
    _order = "start_date desc, mandate_category_id"

    _inactive_cascade = True
    _unicity_keys = "N/A"
    _sql_constraints = [
        (
            "date_check",
            "CHECK(start_date <= deadline_date)",
            "The start date must be anterior to the deadline date.",
        ),
        (
            "date_check2",
            "CHECK((end_date is NULL) or ((start_date <= end_date) and \
         (end_date <= deadline_date)))",
            "The end date must be between start date and deadline date.",
        ),
    ]

    unique_id = fields.Integer(
        compute="_compute_unique_id", string="Unique ID", store=True
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Representative",
        required=True,
        index=True,
        auto_join=True,
        tracking=True,
    )
    instance_id = fields.Many2one(
        string="Instance Mandate Descendant of",
        # overwrite in children with the assembly, but mus be set to something
        comodel_name="int.instance",
        store=True,
    )
    mandate_category_id = fields.Many2one(
        comodel_name="mandate.category",
        string="Mandate Category",
        required=True,
        index=True,
        tracking=True,
    )
    designation_int_assembly_id = fields.Many2one(
        comodel_name="int.assembly",
        string="Designation Assembly",
        index=True,
        tracking=True,
        domain=[("is_designation_assembly", "=", True)],
    )
    start_date = fields.Date(required=True, tracking=True)
    deadline_date = fields.Date(required=True, tracking=True)
    end_date = fields.Date(default=False, tracking=True)
    with_remuneration = fields.Boolean()
    with_revenue_declaration = fields.Boolean(
        help="Representative is subject to a declaration of income",
    )
    with_assets_declaration = fields.Boolean(
        help="Representative is subject to a declaration of assets",
    )
    alert_date = fields.Date()

    @api.depends("create_date")
    def _compute_unique_id(self):
        # unique_id as compute and not set in the create because it need
        # to be set as early as possible. It is used in the detect duplicate,
        # which is used it the create of abstract duplicate,
        # and if here we overload the create, the set of unique_id will be
        # too late, since we need the id to be able to set it
        # (so after the create)
        for mandate in self:
            mandate.unique_id = mandate.id + self._unique_id_sequence

    def name_get(self):
        res = []
        for mandate in self:
            display_name = "{name} ({mandate_category})".format(
                name=mandate.partner_id.name,
                mandate_category=mandate.mandate_category_id.name,
            )
            res.append((mandate.id, display_name))
        return res

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            partners = self.env["res.partner"].search([("name", operator, name)])
            categories = self.env["mandate.category"].search([("name", operator, name)])
            return self.search(
                [
                    "|",
                    ("partner_id", "in", partners.ids),
                    ("mandate_category_id", "in", categories.ids),
                ]
                + args,
                limit=limit,
            ).name_get()
        else:
            return super().name_search(
                name=name, args=args, operator=operator, limit=limit
            )

    def action_invalidate(self, vals=None):
        """
        Invalidate mandates
        Use current date if no date is given
        :rparam: True
        :rtype: boolean
        """
        vals = vals or {}
        end_date = vals.get("end_date") or fields.Date.today()
        res = True
        for mandate in self:
            if end_date > mandate.deadline_date:
                vals["end_date"] = mandate.deadline_date
            elif end_date < mandate.start_date:
                vals["end_date"] = mandate.start_date
            else:
                vals["end_date"] = end_date
            res = res and super(AbstractMandate, mandate).action_invalidate(vals=vals)
        return res

    @api.model
    def process_finish_and_invalidate_mandates(self):
        """
        This method is used to finish and invalidate mandates after deadline
        date
        :rparam: True
        :rtype: boolean
        """
        sql_query = """
                SELECT mandate.id
                    FROM %s as mandate
                    WHERE mandate.deadline_date < current_date
                      AND mandate.end_date IS NULL
              """
        self.env.cr.execute(sql_query % self._table)
        mandate_ids = [mandate[0] for mandate in self.env.cr.fetchall()]
        mandates = self.browse(mandate_ids)

        if mandate_ids:
            mandates.action_invalidate()

        return True

    @api.onchange("mandate_category_id")
    def _onchange_mandate_category_id(self):
        for mandate in self:
            mandate.with_remuneration = mandate.mandate_category_id.with_remuneration
            mandate.with_revenue_declaration = (
                mandate.mandate_category_id.with_revenue_declaration
            )
            mandate.with_assets_declaration = (
                mandate.mandate_category_id.with_assets_declaration
            )
