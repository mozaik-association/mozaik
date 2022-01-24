# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from typing import List

import pydantic

from odoo.addons.pydantic import models

from .petition_registration_answer import PetitionRegistrationAnswer


class PetitionRegistration(models.BaseModel):
    lastname: str
    firstname: str
    email: str
    mobile: str
    zip: str
    country_id: int
    date_open: date
    petition_id: int
    list_answer: List[PetitionRegistrationAnswer] = pydantic.Field(
        [], alias="petition_registration_answer_ids"
    )
