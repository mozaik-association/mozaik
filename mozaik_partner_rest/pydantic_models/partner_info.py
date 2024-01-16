# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date, datetime
from typing import List

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.mozaik_country_rest.pydantic_models.country_info import CountryInfo
from odoo.addons.mozaik_country_rest.pydantic_models.country_state_info import (
    CountryStateInfo,
)
from odoo.addons.mozaik_involvement_rest.pydantic_models.involvement_info import (
    InvolvementInfo,
)
from odoo.addons.mozaik_membership_rest.pydantic_models.membership_line_info import (
    MembershipLineInfo,
)
from odoo.addons.mozaik_membership_rest.pydantic_models.subscription_info import (
    SubscriptionInfo,
)
from odoo.addons.pydantic import utils

from .address_info import AddressInfo
from .co_residency_info import CoResidencyInfo


class PartnerShortInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str
    email: str = None
    street: str = None
    street2: str = None
    city: str = None
    zip: str = None
    state: CountryStateInfo = pydantic.Field(None, alias="state_id")
    country: CountryInfo = pydantic.Field(None, alias="country_id")
    phone: str = None
    mobile: str = None
    ref: str = None
    write_date: datetime
    city_id: int = None
    address: str = None
    address_addres: AddressInfo = pydantic.Field(None, alias="address_address_id")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class PartnerInfo(PartnerShortInfo):
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
    subscription: SubscriptionInfo = pydantic.Field(
        None, alias="subscription_product_id"
    )
    co_residency: CoResidencyInfo = pydantic.Field(None, alias="co_residency_id")
