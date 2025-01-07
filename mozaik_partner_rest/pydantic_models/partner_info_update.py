# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from typing import List

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class PartnerInfoUpdate(BaseModel, metaclass=ExtendableModelMeta):

    email: str = None
    city: str = None
    zip: str = None
    state_id: int = None
    phone: str = None
    mobile: str = None
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
    unemployed: bool = None
    gender: str = None
    disabled: bool = None
    global_opt_out: bool = None
    update_instance: bool = None
