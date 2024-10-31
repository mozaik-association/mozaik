# Copyright 2024 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils

from .document_folder_info import DocumentFolderInfo


class DocumentInfo(BaseModel, metaclass=ExtendableModelMeta):

    id: int
    name: str
    create_date: datetime
    write_date: datetime
    folder: DocumentFolderInfo = pydantic.Field(None, alias="folder_id")
    content_filename: str = None
    content_filesize: int = 0
    url: str = None

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class DocumentWithContentInfo(DocumentInfo):
    content: str
