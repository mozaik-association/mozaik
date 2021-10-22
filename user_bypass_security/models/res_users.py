# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):

    _inherit = "res.users"

    @api.model
    def _apply_ir_rules(self, query, mode="read"):
        """
        Bypass rules if requested by a special context key
        """
        if self.env.context.get("bypass_ir_rule_read") == "1" and mode == "read":
            _logger.debug("Escape _apply_ir_rules for %s mode=read", self._name)
            return
        super()._apply_ir_rules(query, mode=mode)

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        # For the drop down list, we want the user to only see the users
        # he can really see (without by passing ir rules)
        if self.env.context.get("bypass_ir_rule_read"):
            self = self.with_context(bypass_ir_rule_read=None)
        return super(ResUsers, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )
