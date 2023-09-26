# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from psycopg2.extensions import AsIs

from odoo import _, api, fields, models

CATEGORY_TYPE = [
    ("petition", "Petition"),
    ("voluntary", "Voluntary Work"),
    ("newsletter", "Newsletter"),
    ("notification", "Notification"),
]

_logger = logging.getLogger(__name__)


class PartnerInvolvementCategory(models.Model):

    _name = "partner.involvement.category"
    _inherit = [
        "mozaik.abstract.model",
        "owner.mixin",
    ]
    _description = "Partner Involvement Category"
    _terms = ["interest_ids"]
    _unicity_keys = "name"

    @api.model
    def _default_res_users_ids(self):
        return self.env.user

    name = fields.Char(
        string="Involvement Category",
        required=True,
        tracking=True,
    )
    code = fields.Char(
        copy=False,
        tracking=True,
    )
    note = fields.Text(
        string="Notes",
        tracking=True,
    )
    involvement_type = fields.Selection(
        selection=CATEGORY_TYPE,
        string="Type",
        index=True,
        tracking=True,
    )
    allow_multi = fields.Boolean(
        string="Allow Multiple Involvements",
        default=False,
        tracking=True,
    )
    # Owners come from mixin. Rename columns
    res_users_ids = fields.Many2many(
        relation="involvement_category_res_users_rel",
        column1="category_id",
        column2="user_id",
    )
    interest_ids = fields.Many2many(
        comodel_name="thesaurus.term",
        relation="involvement_category_term_interests_rel",
        column1="category_id",
        column2="term_id",
        string="Interests",
    )
    involvement_ids = fields.One2many(
        comodel_name="partner.involvement",
        inverse_name="involvement_category_id",
        string="Involvements",
    )
    importance_level = fields.Selection(
        [("low", "Low"), ("high", "High")],
        string="Importance Level",
        default="low",
        required=True,
    )

    def init(self):
        """
        Create unique index based on code for active records.
        :return:
        """
        result = super().init()

        cr = self.env.cr
        createit = True
        index_name = "%s_unique_code_idx" % self._table
        index_def = (
            "CREATE UNIQUE INDEX %(index)s ON %(table)s "
            "USING btree (code) WHERE (active IS TRUE)"
        )
        index_values = {
            "index": AsIs(index_name),
            "table": AsIs(self._table),
        }
        query = """
            SELECT indexdef
            FROM pg_indexes
            WHERE tablename = %s AND indexname = %s"""
        cr.execute(query, (self._table, index_name))
        sql_res = cr.dictfetchone()
        if sql_res:
            previous = sql_res.get("indexdef", "").replace(" ON public.", " ON ")
            current = index_def % index_values
            if previous != current:
                _logger.info(
                    "Rebuild index %s_unique_idx:\n%s\n%s",
                    index_name,
                    previous,
                    current,
                )
                drop_values = {
                    "index": AsIs(index_name),
                }
                cr.execute("DROP INDEX %(index)s", drop_values)
            else:
                createit = False

        if createit:
            cr.execute(index_def, index_values)

        return result

    def write(self, vals):
        """
        Force an effective time on an allow_multi category
        """
        self.ensure_one()
        if vals.get("allow_multi"):
            invs = self.mapped("involvement_ids").filtered(
                lambda s: not s.effective_time
            )
            invs.write({"effective_time": fields.Datetime.now()})
        res = super().write(vals)
        return res

    def copy(self, default=None):
        """
        Mark the name as (copy)
        Retrieve owner list if possible
        """
        default = default or {}
        default["name"] = _("%s (copy)") % self.name
        if self.env.user in self.res_users_ids:
            default["res_users_ids"] = [(6, 0, self.res_users_ids.ids)]
        res = super().copy(default=default)
        return res

    @api.onchange("involvement_type")
    def _onchange_involvement_type(self):
        self.allow_multi = False
