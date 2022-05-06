# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from typing import List

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.mozaik_country_rest.pydantic_models.country_info import CountryInfo
from odoo.addons.mozaik_distribution_list_rest.pydantic_models.distribution_list_info import (
    DistributionListInfo,
)
from odoo.addons.mozaik_involvement_rest.pydantic_models.involvement_category_info import (
    InvolvementCategoryInfo,
)
from odoo.addons.mozaik_thesaurus_api.pydantic_models.thesaurus_term_info import (
    ThesaurusTermInfo,
)
from odoo.addons.partner_rest_api.pydantic_models.partner_info import PartnerInfo
from odoo.addons.pydantic import utils


class MembershipRequestInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    lastname: str
    firstname: str = None
    gender: str = None
    street_man: str = None
    street2: str = None
    zip_man: str = None
    city_man: str = None
    request_type: str = None
    number: str = None
    box: str = None
    local_only: str = None
    day: str = None
    month: str = None
    year: str = None
    email: str = None
    mobile: str = None
    phone: str = None
    interests: List[ThesaurusTermInfo] = pydantic.Field([], alias="interest_ids")
    competencies: List[ThesaurusTermInfo] = pydantic.Field([], alias="competency_ids")
    indexation_comments: str = None
    note: str = None
    distribution_lists: List[DistributionListInfo] = pydantic.Field(
        [], alias="distribution_list_ids"
    )
    is_company: bool = False
    involvement_categories: List[InvolvementCategoryInfo] = pydantic.Field(
        [], alias="involvement_category_ids"
    )
    local_voluntary: str = None
    regional_voluntary: str = None
    national_voluntary: str = None
    amount: float = None
    reference: str = None
    effective_time: datetime = None
    nationality: CountryInfo = pydantic.Field(None, alias="nationality_id")
    country: CountryInfo = pydantic.Field(None, alias="country_id")
    city_id: int = None
    partner: PartnerInfo = pydantic.Field(None, alias="partner_id")
    unemployed_change: str = None
    disabled_change: str = None
    write_date: datetime
    payment_link: str = None

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
