# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils


class MembershipRequestOriginInfo(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
