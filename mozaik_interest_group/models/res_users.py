# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResUsers(models.Model):

    _inherit = "res.users"

    def _interest_groups(self):
        """
        Cache the interest_group_user_ids domain result,
        for a user on which security on interest groups applies.
        """
        self.ensure_one()
        self_sudo = self.sudo().with_context(active_test=False)
        dom = [("id", "child_of", self.interest_group_user_ids.ids)]
        interest_groups = self_sudo.env["interest.group"].search(dom)
        return interest_groups.ids

    def _dont_apply_security_on_interest_groups(self):
        """
        Returns 0 if security on interest groups applies to this user,
        1 otherwise.
        Aim: use it inside a domain leaf to build a TRUE_LEAF or a FALSE_LEAF
        (see odoo/osv/expression.py)
        """
        self.ensure_one()
        return 0 if self.apply_security_on_interest_groups else 1
