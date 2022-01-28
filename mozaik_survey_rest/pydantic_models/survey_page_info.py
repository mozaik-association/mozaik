# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.pydantic import models, utils


class SurveyPageInfo(models.BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
