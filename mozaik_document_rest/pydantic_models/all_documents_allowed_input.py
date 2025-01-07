# Copyright 2024 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class AllDocumentsAllowedInput(BaseModel, metaclass=ExtendableModelMeta):

    partner_id: int = None
