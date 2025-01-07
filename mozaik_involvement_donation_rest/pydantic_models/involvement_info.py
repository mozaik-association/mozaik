# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date

from odoo.addons.mozaik_involvement_rest.pydantic_models.involvement_info import (
    InvolvementInfo as BaseInvolvementInfo,
)


class InvolvementInfo(BaseInvolvementInfo, extends=BaseInvolvementInfo):
    amount: float = None
    reference: str = None
    payment_date: date = None
