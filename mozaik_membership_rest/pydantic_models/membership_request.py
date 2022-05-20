# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from typing import List

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class MembershipRequest(BaseModel, metaclass=ExtendableModelMeta):
    lastname: str
    firstname: str
    request_type: str
    partner_id: int = None
    gender: str = None
    street: str = None
    street2: str = None
    number: str = None
    box: str = None
    zip: str = None
    city: str = None
    local_only: str = None
    day: int = None
    month: int = None
    year: int = None
    email: str = None
    mobile: str = None
    phone: str = None
    interest_ids: List[int] = []
    competency_ids: List[int] = []
    indexation_comments: str = None
    note: str = None
    distribution_list_ids: List[int] = []
    is_company: bool = None
    involvement_category_ids: List[int] = []
    involvement_category_codes: List[str] = []
    local_voluntary: str = None
    regional_voluntary: str = None
    national_voluntary: str = None
    amount: float = None
    reference: str = None
    effective_time: datetime = None
    nationality_id: int = None
    city_id: int = None
    country_id: int = None
    unemployed_change: str = None
    disabled_change: str = None
    force_global_opt_out: bool = None
    force_global_opt_in: bool = None
    auto_validate: bool = False
    force_auto_validate: bool = False
    auto_generate_reference: bool = False
    auto_validate_after_payment: bool = False
