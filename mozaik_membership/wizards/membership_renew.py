# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import api, fields, models


class MembershipRenew(models.TransientModel):
    """
    Wizard used to help users to renew selected/existing membership.line
    """

    _name = "membership.renew"
    _description = "Renew membership line"

    membership_line_ids = fields.Many2many(
        comodel_name="membership.line",
        string="Lines",
        help="Lines to renew existing subscription",
        domain=[("active", "=", True)],
    )
    date_from = fields.Date(
        default=fields.Date.today(),
        help="Start date of new membership lines",
    )

    @api.model
    def default_get(self, fields_list):
        """
        Load line given by context (active_domain or active_ids)
        Allowed active model:
        - membership.line
        - res.partner
        :param fields_list: list of str
        :return: dict
        """
        result = super(MembershipRenew, self).default_get(fields_list)
        context = self.env.context
        active_model = context.get("active_model")
        active_ids = context.get("active_ids")
        allowed_models = [
            self.membership_line_ids._name,
            "res.partner",
        ]
        if active_model in allowed_models and active_ids:
            target_obj = self.env[active_model]
            # Load from context
            targets = target_obj.browse(active_ids)
            # If it membership.line, just rename for better understanding
            if active_model == self.membership_line_ids._name:
                lines = targets
            else:  # We work on res.partner
                lines = targets.mapped("membership_line_ids").filtered(
                    lambda line: line.active and line.state_code == "member"
                )
            result.update(
                {
                    "membership_line_ids": [(6, False, lines.ids)],
                }
            )
        return result

    def action_close_and_renew(self):
        """
        Action to close existing
        :return: dict
        """
        self.ensure_one()
        lines = self._action_close_and_renew()
        action = (
            self.sudo().env.ref("mozaik_membership.membership_line_action").read()[0]
        )
        domain = [("id", "in", lines.ids)]
        action.update(
            {
                "domain": domain,
                "context": {},
            }
        )
        return action

    def _action_close_and_renew(self):
        """
        Close membership lines and renew them automatically

        If active_ids, then ignore active_domain
        :return: membership.line recordset
        """
        self.ensure_one()
        date_to = fields.Date.from_string(self.date_from) - timedelta(days=1)
        renewed_lines = self.membership_line_ids._close(
            date_to=fields.Date.to_string(date_to)
        )
        if renewed_lines:
            active_domain = self.env.context.get("active_domain", False)
            if self.env.context.get("active_ids", False):
                active_domain = False
            renewed_lines.with_context(active_domain=active_domain)._renew(
                date_from=self.date_from
            )
        return renewed_lines
