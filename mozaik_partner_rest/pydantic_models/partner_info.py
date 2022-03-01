# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from typing import List

import pydantic

from odoo.addons.mozaik_involvement_rest.pydantic_models.involvement_info import (
    InvolvementInfo,
)
from odoo.addons.mozaik_membership_rest.pydantic_models.membership_line_info import (
    MembershipLineInfo,
)
from odoo.addons.partner_rest_api.pydantic_models.partner_info import (
    PartnerInfo as BasePartnerInfo,
    PartnerShortInfo as BasePartnerShortInfo,
)

from .address_info import AddressInfo


class PartnerShortInfo(BasePartnerShortInfo, extends=BasePartnerShortInfo):
    city_id: int = None
    address: str = None
    address_addres: AddressInfo = pydantic.Field(None, alias="address_address_id")


class PartnerInfo(BasePartnerInfo, extends=BasePartnerInfo):
    firstname: str = None
    lastname: str = None
    birthdate: date = pydantic.Field(None, alias="birthdate_date")
    int_instance_ids: List[int] = []
    unemployed: bool = None
    gender: str = None
    disabled: bool = None
    master_id: int = None
    subordinate_ids: List[int] = []
    membership_lines: List[MembershipLineInfo] = pydantic.Field(
        [], alias="membership_line_ids"
    )
    involvements: List[InvolvementInfo] = pydantic.Field(
        [], alias="partner_involvement_ids"
    )
    global_opt_out: bool = None
    reference: str = None
