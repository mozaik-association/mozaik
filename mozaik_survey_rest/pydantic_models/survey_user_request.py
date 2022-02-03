# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from typing import Dict, List, Union

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class SurveyUserInputRequest(BaseModel, metaclass=ExtendableModelMeta):
    user_input_lines: Dict[str, Union[str, List[str], Dict[str, List[str]]]]
