# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from typing import List

from odoo.addons.partner_rest_api.pydantic_models.partner_info_update import (
    PartnerInfoUpdate as BasePartnerInfoUpdate,
)


class PartnerInfoUpdate(BasePartnerInfoUpdate, extends=BasePartnerInfoUpdate):
    firstname: str = None
    lastname: str = None
    birthdate_date: date = None
    master_id: int = None
    address_address_id: int = None
    street: str = None
    street2: str = None
    number: str = None
    box: str = None
    city_id: int = None
    country_id: int = None
    subordinate_ids: List[int] = None
    disabled: bool = None
    global_opt_out: bool = None
