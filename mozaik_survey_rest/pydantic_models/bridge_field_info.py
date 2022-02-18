# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils


class BridgeFieldInfo(BaseModel, metaclass=ExtendableModelMeta):
    name: str

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
