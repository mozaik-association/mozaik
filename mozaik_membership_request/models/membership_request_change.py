##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import fields, models


class MembershipRequestChange(models.Model):
    _name = "membership.request.change"
    _inherit = ["mozaik.abstract.model"]
    _description = "Membership Request Change"
    _order = "sequence"
    _unicity_keys = "N/A"

    membership_request_id = fields.Many2one(
        comodel_name="membership.request",
        string="Membership Request",
        ondelete="cascade",
    )
    sequence = fields.Integer(string="Sequence")
    field_name = fields.Char(string="Field Name")
    old_value = fields.Char(string="Old Value")
    new_value = fields.Char(string="New Value")
