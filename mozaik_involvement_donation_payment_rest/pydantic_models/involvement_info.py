# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.mozaik_involvement_donation_rest.pydantic_models.involvement_info import (
    InvolvementInfo as BaseInvolvementInfo,
)


class InvolvementInfo(BaseInvolvementInfo, extends=BaseInvolvementInfo):
    payment_link: str = None
