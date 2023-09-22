# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from psycopg2.extensions import AsIs

from odoo import _, api, exceptions, fields, models

from .partner_involvement_category import CATEGORY_TYPE

CATEGORY_TYPE_CODES = [elem[0] for elem in CATEGORY_TYPE]

_logger = logging.getLogger(__name__)


class PartnerInvolvement(models.Model):

    _name = "partner.involvement"
    _inherit = ["mozaik.abstract.model"]
    _description = "Partner Involvement"
    _rec_name = "involvement_category_id"
    _order = "partner_id, importance_level, creation_time desc"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        index=True,
        tracking=True,
        domain=[("is_assembly", "=", False)],
        auto_join=True,
    )
    involvement_category_id = fields.Many2one(
        comodel_name="partner.involvement.category",
        string="Involvement Category",
        required=True,
        index=True,
        tracking=True,
    )
    note = fields.Text(
        string="Notes",
        tracking=True,
    )
    involvement_type = fields.Selection(
        related="involvement_category_id.involvement_type",
        store=True,
        readonly=True,
        index=True,
    )
    allow_multi = fields.Boolean(
        related="involvement_category_id.allow_multi",
        string="Allow Multiple Involvements",
        store=True,
        readonly=True,
    )
    effective_time = fields.Datetime(
        string="Involvement Date",
        copy=False,
        tracking=True,
    )
    creation_time = fields.Datetime(
        string="Involvement Date (Creation)",
        compute="_compute_creation_time",
        store=True,
    )
    importance_level = fields.Selection(
        related="involvement_category_id.importance_level", store=True
    )

    @api.constrains("effective_time")
    def _check_effective_time_set(self):
        for rec in self:
            if (
                rec.active
                and rec.allow_multi
                and (
                    not rec.involvement_type
                    or rec.involvement_type in CATEGORY_TYPE_CODES
                )
                and not rec.effective_time
            ):
                raise exceptions.UserError(
                    _("Effective time is mandatory for this kind of involvement !")
                )

    @api.depends("effective_time")
    def _compute_creation_time(self):
        for involvement in self:
            if involvement.effective_time:
                involvement.creation_time = involvement.effective_time
            else:
                involvement.creation_time = involvement.create_date

    def init(self):
        """
        Create unique indexes based on partner_id and involvement_category_id
        for active records.
        Do not call super() here
        :return:
        """
        cr = self.env.cr

        index_values = {
            "table": AsIs(self._table),
        }

        def create_index(index_def, index_name):
            createit = True
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

                    drop_value = {
                        "index": AsIs(index_name),
                    }
                    cr.execute("DROP INDEX %(index)s", drop_value)
                else:
                    createit = False
            if createit:
                cr.execute(index_def, index_values)

        def1 = (
            "CREATE UNIQUE INDEX %(table)s_unique_1_idx "
            "ON %(table)s USING btree "
            "(partner_id, involvement_category_id) "
            "WHERE ((active IS TRUE) AND (allow_multi IS FALSE))"
        )
        ndx1 = "%s_unique_1_idx" % self._table
        create_index(def1, ndx1)

        # NB: donation involvements were moved to mozaik_involvement_donation
        # but we keep this index AsIs because it would be too complex to refactor it
        def2 = (
            "CREATE UNIQUE INDEX %(table)s_unique_2_idx "
            "ON %(table)s USING btree "
            "(partner_id, involvement_category_id, effective_time) "
            "WHERE ((active IS TRUE) AND (allow_multi IS TRUE) "
            "AND (((involvement_type)::text <> 'donation'::text) OR "
            "(involvement_type IS NULL)))"
        )
        ndx2 = "%s_unique_2_idx" % self._table
        create_index(def2, ndx2)

    def _add_followers(self):
        """
        Add to the mail_followers table the followers of the involvement
        category, but only if they are not already following the involvement.
        """
        to_follow = self.involvement_category_id.message_follower_ids.mapped(
            "partner_id"
        ).ids
        already_following = self.message_follower_ids.mapped("partner_id").ids

        for foll_id in list(set(to_follow).difference(set(already_following))):
            self.env["mail.followers"].create(
                {
                    "res_model": "partner.involvement",
                    "res_id": self.id,
                    "partner_id": foll_id,
                }
            )

    @api.model
    @api.returns("self", lambda value: value.id)
    def create(self, vals):
        """
        Add interests to partner when creating an involvement
        Set effective date if any
        Add all followers of the involvement category as followers
        of the involvement itself.
        """
        if not vals.get("effective_time"):
            ic = self.env["partner.involvement.category"].browse(
                vals["involvement_category_id"]
            )
            if ic.allow_multi and (
                not ic.involvement_type or ic.involvement_type in CATEGORY_TYPE_CODES
            ):
                vals["effective_time"] = fields.Datetime.now()
        res = super(PartnerInvolvement, self).create(vals)
        terms = res.involvement_category_id.interest_ids
        if terms:
            interests = [(4, term.id) for term in terms]
            res.partner_id.sudo().write({"interest_ids": interests})
        res.sudo()._add_followers()
        return res

    def copy(self, default=None):
        self.ensure_one()
        if self.active and not self.allow_multi:
            raise exceptions.UserError(_("An active involvement cannot be duplicated."))
        res = super(PartnerInvolvement, self).copy(default=default)
        return res

    @api.onchange("allow_multi")
    def _onchange_allow_multi(self):
        if (
            self.allow_multi
            and not self.involvement_type
            or self.involvement_type in CATEGORY_TYPE_CODES
            and not self.effective_time
        ):
            self.effective_time = fields.Datetime.now()
