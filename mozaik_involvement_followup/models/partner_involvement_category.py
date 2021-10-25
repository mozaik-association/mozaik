# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PartnerInvolvementCategory(models.Model):

    _inherit = "partner.involvement.category"

    nb_deadline_days = fields.Integer(
        string="Number of days before deadline",
        default=0,
        tracking=True,
        help="0 = no follow-up on children involvements",
    )

    mandate_category_id = fields.Many2one(
        "mandate.category",
        string="Mandate Category",
        domain=[("type", "=", "int")],
        index=True,
        tracking=True,
    )

    involvement_category_ids = fields.Many2many(
        "partner.involvement.category",
        relation="partner_involvement_category_followup_rel",
        column1="partner_id",
        column2="followup_category_id",
        string="Follow-up Categories",
        domain=[("involvement_type", "in", [False, "voluntary"])],
    )

    parent_involvement_category_ids = fields.Many2many(
        "partner.involvement.category",
        relation="partner_involvement_category_followup_rel",
        column2="partner_id",
        column1="followup_category_id",
        string="Parent Categories",
        help="Categories specifying this category as follow-up category",
    )

    _sql_constraints = [
        (
            "nb_deadline_days_no_negative",
            "CHECK (nb_deadline_days >= 0)",
            "Number of days before deadline cannot be negative !",
        ),
        (
            "mandate_category_without_deadline",
            "CHECK (mandate_category_id IS NULL OR nb_deadline_days > 0)",
            "Without deadline rule mandate category must be null !",
        ),
    ]

    @api.constrains("involvement_category_ids")
    def _check_involvement_category_ids_recursion(self):
        """
        :raise ValidationError: when a recursion is detected
        """
        if not self._check_m2m_recursion("involvement_category_ids"):
            raise ValidationError(
                _("Error! You cannot specify " "recursive set of follow-up categories.")
            )
        return True

    @api.constrains("involvement_type")
    def _check_involvement_category_followup_without_type(self):
        """
        :raise ValidationError: when a typed category is used
                                as followup category
        """
        for ic in self.filtered(
            lambda s: s.involvement_type not in [False, "voluntary"]
        ):
            if ic.parent_involvement_category_ids:
                raise ValidationError(
                    _("Error! Followup category cannot be of this type")
                )
        return True

    @api.onchange("nb_deadline_days")
    def _onchange_nb_deadline_days(self):
        if not self.nb_deadline_days:
            self.mandate_category_id = False
            self.involvement_category_ids = False

    @api.model
    def read_followers_data(self, follower_ids):
        """
        Disable security for this method but recompute is_uid properties
        """
        result = super(PartnerInvolvementCategory, self.sudo()).read_followers_data(
            follower_ids
        )
        is_editable = self.user_has_groups("mozaik_base.mozaik_res_groups_configurator")
        uid = self.env.user.partner_id.id
        for res in result:
            res[2]["is_editable"] = is_editable
            res[2]["is_uid"] = uid == res[0]
        return result

    @api.model
    @api.returns("self", lambda value: value.id)
    def create(self, vals):
        """
        Protect use of followup categories delegating rules check
        to the specified followup categories (mode=write)
        """
        res = super(PartnerInvolvementCategory, self).create(vals)
        if vals.get("involvement_category_ids"):
            res.involvement_category_ids.check_access_rule("write")
        return res

    def write(self, vals):
        """
        Protect use of followup categories delegating rules check
        to the specified followup categories (mode=write)
        """
        res = super(PartnerInvolvementCategory, self).write(vals)
        if vals.get("involvement_category_ids"):
            self.mapped("involvement_category_ids").check_access_rule("write")
        return res
