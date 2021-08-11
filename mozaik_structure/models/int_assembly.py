# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IntAssembly(models.Model):

    _name = "int.assembly"
    _inherit = ["abstract.assembly"]
    _description = "Internal Assembly"

    assembly_category_id = fields.Many2one(
        comodel_name="int.assembly.category",
    )
    instance_id = fields.Many2one(
        comodel_name="int.instance",
    )
    is_designation_assembly = fields.Boolean(
        tracking=True,
    )
    is_secretariat = fields.Boolean(
        related="assembly_category_id.is_secretariat",
        store=True,
    )

    @api.model
    def _get_names(self, vals=None):
        """
        Get the tuple of names needed to build the assembly name
        :param values: dict
        :return: tuple of string
        """
        n1 = (
            self
            and self.instance_id
            or self.env["int.instance"].browse(vals and vals.get("instance_id"))
        ).name or False
        n2 = (
            self
            and self.assembly_category_id
            or self.env["int.assembly.category"].browse(
                vals and vals.get("assembly_category_id")
            )
        ).name or False
        return (n1, n2)

    def _get_secretariat(self):
        """
        Get the secretariat related to the same instance as
        the given assembly
        """
        self.ensure_one()
        if self.is_secretariat:
            return self
        secretariat = self.instance_id._get_secretariat()
        return secretariat
