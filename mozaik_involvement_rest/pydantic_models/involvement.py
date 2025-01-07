# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class Involvement(BaseModel, metaclass=ExtendableModelMeta):
    partner_id: int
    involvement_category_id: int
    effective_time: datetime = None
