# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import Optional

from extendable_pydantic import ExtendableModelMeta  # pylint:disable=W7936
from pydantic import Field  # pylint:disable=W7936

from odoo.addons.pydantic import utils

from .employee_info import EmployeeInfo
from .partner_min import PartnerMin


class EmployeeDetail(EmployeeInfo, metaclass=ExtendableModelMeta):
    work_phone: Optional[str] = None
    work_email: Optional[str] = None
    image_1920_url: Optional[str] = None
    address: Optional[PartnerMin] = Field(None, alias="address_id")
    work_location: Optional[str] = None

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter
