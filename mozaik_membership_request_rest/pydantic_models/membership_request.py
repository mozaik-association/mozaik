# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import List

from odoo.addons.pydantic import models


class MembershipRequest(models.BaseModel):
    lastname: str
    firstname: str
    gender: str
    street_man: str
    zip_man: str
    city_man: str
    request_type: str
    number: str = None
    box: str = None
    local_only: bool
    day: int = None
    month: int = None
    year: int = None
    email: str = None
    mobile: str = None
    phone: str = None
    interest_ids: List[int] = None
    competency_ids: List[int] = None
    note: str = None
    distribution_list_ids: List[int] = None
    is_company: bool = False
    involvement_category_ids: List[int] = None
    local_voluntary: bool = False
    regional_voluntary: bool = False
    national_voluntary: bool = False
    amount: float = None
    reference: str = None
    effective_time: str = None
    local_only: bool = None
    nationality_id: int = None
