# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from datetime import date
from typing import List

import pydantic

from odoo.addons.partner_rest_api.pydantic_models.partner_info import (
    PartnerInfo as BasePartnerInfo,
    PartnerShortInfo as BasePartnerShortInfo,
)


class PartnerInfo(BasePartnerInfo, extends=BasePartnerInfo):
    sponsor: BasePartnerShortInfo = pydantic.Field(None, alias="sponsor_id")
    sponsor_children: List[BasePartnerShortInfo] = pydantic.Field(
        [], alias="sponsor_godchild_ids"
    )
    sponsorship_date: date = None
