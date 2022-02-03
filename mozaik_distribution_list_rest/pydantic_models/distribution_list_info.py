# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils


class DistributionListInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str
    code: str = None
    newsletter: bool = None

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
