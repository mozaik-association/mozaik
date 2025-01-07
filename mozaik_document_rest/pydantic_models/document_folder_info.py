# Copyright 2024 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils


class DocumentFolderInfo(BaseModel, metaclass=ExtendableModelMeta):

    id: int
    name: str
    parent_folder: "DocumentFolderInfo" = pydantic.Field(None, alias="parent_id")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
