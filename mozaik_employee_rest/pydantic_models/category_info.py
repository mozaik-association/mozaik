# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from extendable_pydantic import ExtendableModelMeta  # pylint:disable=W7936
from pydantic import BaseModel  # pylint:disable=W7936

from odoo.addons.pydantic import utils


class CategoryInfo(BaseModel, metaclass=ExtendableModelMeta):
    name: str

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
