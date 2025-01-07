# Copyright 2024 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class NewsInputFilter(BaseModel, metaclass=ExtendableModelMeta):

    partner_id: int = None
    consultation_date: date = pydantic.Field(
        None,
        description="Returns all allowed news visible "
        "on the specified date. If no date, "
        "take today as default value",
    )
