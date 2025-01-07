# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List

import pydantic

from odoo.addons.mozaik_partner_rest.pydantic_models.partner_info import (
    PartnerInfo as BasePartnerInfo,
)

from .membership_line_info import MembershipLineInfo
from .subscription_info import SubscriptionInfo


class PartnerInfo(BasePartnerInfo):
    membership_lines: List[MembershipLineInfo] = pydantic.Field(
        [], alias="membership_line_ids"
    )
    subscription: SubscriptionInfo = pydantic.Field(
        None, alias="subscription_product_id"
    )
