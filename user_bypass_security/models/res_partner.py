# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def _apply_ir_rules(self, query, mode='read'):
        """
        Name of the user is a related on the partner name, so bypass_ir_rule
        need to be also done on the partner
        """
        if self.env.context.get('bypass_ir_rule_read') == '1' \
                and mode == 'read':
            _logger.debug(
                'Escape _apply_ir_rules for %s mode=read', self._name)
            return

        super()._apply_ir_rules(query, mode=mode)
