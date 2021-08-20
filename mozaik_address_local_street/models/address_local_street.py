# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class AddressLocalStreet(models.Model):

    _name = "address.local.street"
    _description = "Local Street"
    _rec_name = "local_street"
    _order = "local_zip,local_street"

    local_zip = fields.Char("Zip", required=True, index=True)
    identifier = fields.Char(required=True, index=True)
    local_street = fields.Char("Street", required=True, index=True)
    local_street_alternative = fields.Char("Alternative Street", index=True)
    disabled = fields.Boolean()

    _sql_constraints = [
        (
            "check_unicity_street",
            "unique(local_zip,identifier)",
            _(
                "This local street identifier already exists for this zip code!"
            ),
        )
    ]

    @api.multi
    def name_get(self):
        """
        If a ``local_street_alternative`` is defined then name must be show
        like this "local_street / local_street_alternative"
        """
        res = []
        for record in self:
            display_name = " / ".join(
                [
                    s
                    for s in [
                        record.local_street,
                        record.local_street_alternative,
                    ]
                    if s
                ]
            )
            res.append((record.id, display_name))
        return res

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            record = self.search(
                [
                    "|",
                    ("local_street", operator, name),
                    ("local_street_alternative", operator, name),
                ]
                + args,
                limit=limit,
            )
        else:
            record = self.search(args, limit=limit)
        return record.name_get()
