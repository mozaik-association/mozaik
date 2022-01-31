# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from typing import List

import pydantic

from odoo.addons.pydantic import models

from .petition_registration_answer import PetitionRegistrationAnswer


class PetitionRegistrationRequest(models.BaseModel):
    lastname: str = None
    firstname: str = None
    email: str = None
    mobile: str = None
    zip: str = None
    date_open: date = date.today()
    answers: List[PetitionRegistrationAnswer] = pydantic.Field([])
