# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields


class Many2manySudoRead(fields.Many2many):
    """
    Read M2M without applying ir_rule for read access
    """
    def read(self, records):
        recs = records.sudo()
        res = super().read(recs)

        # re-store result in right cache
        for record, rec in zip(records, recs):
            record._cache[self.name] = rec._cache[self.name]

        return res
