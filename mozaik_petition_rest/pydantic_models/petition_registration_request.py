# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from typing import List

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from .petition_registration_answer import PetitionRegistrationAnswer


class PetitionRegistrationRequest(BaseModel, metaclass=ExtendableModelMeta):
    lastname: str = None
    firstname: str = None
    email: str
    mobile: str = None
    zip: str = None
    date_open: date = date.today()
    answers: List[PetitionRegistrationAnswer] = pydantic.Field([])
