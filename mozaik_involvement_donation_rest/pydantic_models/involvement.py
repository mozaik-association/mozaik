# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.addons.mozaik_involvement_rest.pydantic_models.involvement import (
    Involvement as BaseInvolvement,
)


class Involvement(BaseInvolvement, extends=BaseInvolvement):
    amount: float = None
    reference: str = None
