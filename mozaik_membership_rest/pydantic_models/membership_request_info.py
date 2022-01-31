# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List

import pydantic

from odoo.addons.mozaik_thesaurus_api.pydantic_models.thesaurus_term_info import (
    ThesaurusTermInfo,
)
from odoo.addons.pydantic import models, utils


class MembershipRequestInfo(models.BaseModel):
    id: int
    lastname: str
    firstname: str = None
    gender: str = None
    street_man: str = None
    zip_man: str = None
    city_man: str = None
    request_type: str = None
    number: str = None
    box: str = None
    local_only: bool = None
    day: int = None
    month: int = None
    year: int = None
    email: str = None
    mobile: str = None
    phone: str = None
    interests: List[ThesaurusTermInfo] = pydantic.Field([], alias="interest_ids")
    local_only: bool = None

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
