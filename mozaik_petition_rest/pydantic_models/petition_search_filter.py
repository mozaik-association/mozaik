# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class PetitionSearchFilter(BaseModel, metaclass=ExtendableModelMeta):
    visible_on_website: bool = None
    date_publish: str = None
