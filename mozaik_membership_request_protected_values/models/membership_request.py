# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    protected_values = fields.Char(
        help="Protected values coming from the REST service."
    )

    @api.model
    def _onchange_partner_id_vals(
        self, is_company, request_type, partner_id, technical_name
    ):
        res = super()._onchange_partner_id_vals(
            is_company,
            request_type,
            partner_id,
            technical_name,
        )
        protected_values = self.env.context.get("protected_values", {})

        if isinstance(protected_values, str):
            try:
                protected_values = safe_eval(protected_values)
            except Exception:  # pylint: disable=broad-except
                _logger.warning(
                    "Invalid protected_values dictionary: %s",
                    protected_values,
                    exc_info=True,
                )
                protected_values = {}

        local_voluntary = protected_values.get("local_voluntary")
        regional_voluntary = protected_values.get("regional_voluntary")
        national_voluntary = protected_values.get("national_voluntary")
        local_only = protected_values.get("local_only")
        value = res
        if local_voluntary is not None:
            value["local_voluntary"] = local_voluntary
        if regional_voluntary is not None:
            value["regional_voluntary"] = regional_voluntary
        if national_voluntary is not None:
            value["national_voluntary"] = national_voluntary
        if local_only is not None:
            value["local_only"] = local_only

        return res
