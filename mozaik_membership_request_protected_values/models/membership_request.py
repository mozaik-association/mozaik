# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

VOLUNTARY_FIELD_NAMES = [
    "local_voluntary",
    "regional_voluntary",
    "national_voluntary",
    "local_only",
]


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

        for field_name in VOLUNTARY_FIELD_NAMES:
            field_value = protected_values.get(field_name)
            if field_value is not None:
                res[field_name] = field_value

        return res
