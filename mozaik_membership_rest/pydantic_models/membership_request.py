# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from typing import List

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class MembershipRequest(BaseModel, metaclass=ExtendableModelMeta):
    lastname: str
    firstname: str
    gender: str
    street_man: str
    zip_man: str
    city_man: str
    request_type: str
    street2: str = None
    number: str = None
    box: str = None
    local_only: bool = None
    day: int = None
    month: int = None
    year: int = None
    email: str = None
    mobile: str = None
    phone: str = None
    interest_ids: List[int] = []
    competency_ids: List[int] = []
    note: str = None
    distribution_list_ids: List[int] = []
    is_company: bool = False
    involvement_category_ids: List[int] = []
    local_voluntary: bool = False
    regional_voluntary: bool = False
    national_voluntary: bool = False
    amount: float = None
    reference: str = None
    effective_time: datetime = None
    local_only: bool = None
    nationality_id: int = None
    country_id: int = None
    unemployed_change: str = None
    auto_validate: bool = False
