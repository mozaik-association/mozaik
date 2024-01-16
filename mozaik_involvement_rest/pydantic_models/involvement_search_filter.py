# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class InvolvementSearchFilter(BaseModel, metaclass=ExtendableModelMeta):

    id: int = None
    partner_id: int = None
    partner_name: str = None
    category_name: str = None
    category_code: str = None
    involvement_type: str = None
