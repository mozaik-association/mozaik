# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, tools, models
from psycopg2.extensions import AsIs


class VirtualTarget(models.Model):
    _name = "virtual.target"
    _description = "Searching Result"
    _inherit = [
        'virtual.master.partner',
        'abstract.virtual.target',
        'abstract.term.finder'
    ]
    _auto = False

    email_coordinate_id = fields.Many2one(
        comodel_name="email.coordinate",
        string="Email coordinate",
    )
    postal_coordinate_id = fields.Many2one(
        comodel_name="postal.coordinate",
        string="Postal coordinate",
    )

    @api.model_cr
    def init(self):
        cr = self.env.cr
        """
        This add an id to all columns of `virtual_master_partner`
        """
        view_name = self._table
        tools.drop_view_if_exists(cr, view_name)
        query = """
CREATE OR REPLACE VIEW %(table_name)s AS (
SELECT
  *,
  CONCAT(partner_id, '/', postal_coordinate_id ,'/', email_coordinate_id) AS id
FROM
    virtual_master_partner
)"""
        query_values = {
            "table_name": AsIs(view_name),
        }
        cr.execute(query, query_values)
