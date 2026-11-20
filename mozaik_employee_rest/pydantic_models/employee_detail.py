# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import Optional

from extendable_pydantic import ExtendableModelMeta  # pylint:disable=W7936
from pydantic import Field  # pylint:disable=W7936

from odoo.addons.mozaik_partner_rest.pydantic_models.partner_info import (
    PartnerShortInfo,
)
from odoo.addons.pydantic import utils

from .employee_info import EmployeeInfo


class EmployeeDetail(EmployeeInfo, metaclass=ExtendableModelMeta):
    address: Optional[PartnerShortInfo] = Field(None, alias="address_id")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
