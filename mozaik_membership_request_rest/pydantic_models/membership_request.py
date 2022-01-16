# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.pydantic import models, utils
from typing import (List)

class MembershipRequest(models.BaseModel):
    lastname: str
    firstname: str
    gender: str
    street_man: str
    zip_man: str
    city_man: str
    request_type: str
    number: str
    box: str
    local_only: bool
    day: int
    month: int
    year: int
    email: str
    mobile: str
    phone: str
    interest_ids: List[int]
    competency_ids: List[int]
    note: str
    newsletters: bool
    is_company: bool
    #involvements: List[int]
    local_voluntary: bool
    regional_voluntary: bool
    national_voluntary: bool
    amount: float
    reference: str
    autovalidate: bool
    effective_time: str
    local_only: bool
    nationality_id: int
    #journal: bool
    #indexation_comments: str





