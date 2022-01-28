# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from typing import Dict, List, Union

from odoo.addons.pydantic import models, utils


class SurveyUserInputRequest(models.BaseModel):
    user_input_lines: Dict[str, Union[str, List[str], Dict[str, List[str]]]]

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
