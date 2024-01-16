# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils


class SurveyQuestionAnswerInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    value: str
    write_date: datetime

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
