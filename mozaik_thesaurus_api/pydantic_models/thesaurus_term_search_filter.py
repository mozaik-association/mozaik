# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class ThesaurusTermSearchFilter(BaseModel, metaclass=ExtendableModelMeta):

    id: int = None
    name: str = None
    active: bool = None
    main_term: bool = None
