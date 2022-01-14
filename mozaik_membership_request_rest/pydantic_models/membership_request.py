# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.pydantic import models, utils
from datetime import datetime

class MembershipRequest(models.BaseModel):
    lastname: str
    firstname: str
    gender: str
    local_only: bool
    request_type: str
    distribution_list_ids: int
    day: int
    month: int
    year: int
    nationality_id: int #many2one
    phone: str
    mobile: str
    email: str
    country_id: int #many2one
    address_local_street_id: int #many2one
    zip_man: str
    street_man: str
    street2: str
    number: str
    box: str
    autovalidate: bool
