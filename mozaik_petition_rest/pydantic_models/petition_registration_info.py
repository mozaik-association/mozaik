# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils

from .petition_info import PetitionInfo


class PetitionRegistrationInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    firstname: str = None
    lastname: str = None
    email: str
    petition: PetitionInfo = pydantic.Field(..., alias="petition_id")
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
