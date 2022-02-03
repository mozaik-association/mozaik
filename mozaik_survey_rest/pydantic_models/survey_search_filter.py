# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from typing import List

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class SurveySearchFilter(BaseModel, metaclass=ExtendableModelMeta):

    id: int = None
    title: str = None
    users_login_required: bool = None
    is_private: bool = None
    int_instance_id: int = None
    publish_date_before: date = None
    publish_date_after: date = None
    interest_ids: List[int] = []
