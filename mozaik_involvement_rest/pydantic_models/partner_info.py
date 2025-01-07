# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List

import pydantic

from odoo.addons.mozaik_partner_rest.pydantic_models.partner_info import (
    PartnerInfo as BasePartnerInfo,
)

from .involvement_info import InvolvementInfo


class PartnerInfo(BasePartnerInfo):
    involvements: List[InvolvementInfo] = pydantic.Field(
        [], alias="partner_involvement_ids"
    )
