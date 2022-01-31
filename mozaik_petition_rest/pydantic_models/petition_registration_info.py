# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pydantic

from odoo.addons.pydantic import models, utils

from .petition_info import PetitionInfo


class PetitionRegistrationInfo(models.BaseModel):
    id: int
    firstname: str = None
    lastname: str = None
    email: str = None
    petition: PetitionInfo = pydantic.Field(..., alias="petition_id")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
