# Copyright 2024 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils


class NewsInfo(BaseModel, metaclass=ExtendableModelMeta):

    id: int
    name: str
    start_date: date
    end_date: date or None = None
    content: str or None = None
    image: str or None = None

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
