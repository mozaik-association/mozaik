# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import api, fields, models


class VirtualAssemblyInstance(models.Model):
    _name = "virtual.assembly.instance"
    _description = "Assembly/Instance"
    _inherit = [
        "abstract.virtual.model",
    ]
    _auto = False
    _terms = [
        "competency_ids",
    ]

    int_instance_id = fields.Many2one(
        store=True,
        search=None,
    )
    partner_id = fields.Many2one(
        domain=[("is_assembly", "=", False)],
    )
    model = fields.Char()
    category = fields.Char(
        string="Assembly category",
    )
    int_power_level_id = fields.Many2one(
        comodel_name="int.power.level",
        string="Internal Power Level",
    )
    sta_power_level_id = fields.Many2one(
        comodel_name="sta.power.level",
        string="State Power Level",
    )
    int_category_assembly_id = fields.Many2one(
        comodel_name="int.assembly.category",
        string="Internal Assembly Category",
    )
    ext_category_assembly_id = fields.Many2one(
        comodel_name="ext.assembly.category",
        string="External Assembly Category",
    )
    sta_category_assembly_id = fields.Many2one(
        comodel_name="sta.assembly.category",
        string="State Assembly Category",
    )

    @api.model
    def _get_union_parameters(self):
        """
        Overwrite to add type of mandate.category
        :return: list
        """
        result = super(VirtualAssemblyInstance, self)._get_union_parameters()
        result.extend(["int", "sta", "ext"])
        return result

    @api.model
    def _get_query_parameters(self, parameter=False):
        """
        Get dynamic parameters to build the SQL query.
        :param parameter: object
        :return: dict
        """
        values = super()._get_query_parameters(parameter=parameter)
        int_instance_id = ""
        if parameter == "int":
            int_instance_id = "i.id"
        elif parameter == "sta":
            int_instance_id = "i.int_instance_id"
        elif parameter == "ext":
            int_instance_id = "assembly.instance_id"
        int_cat_id = (
            "assembly.assembly_category_id" if parameter == "int" else "NULL::int"
        )
        sta_cat_id = (
            "assembly.assembly_category_id" if parameter == "sta" else "NULL::int"
        )
        ext_cat_id = (
            "assembly.assembly_category_id" if parameter == "ext" else "NULL::int"
        )
        int_power_id = "i.power_level_id" if parameter == "int" else "NULL::int"
        sta_power_id = "i.power_level_id" if parameter == "sta" else "NULL::int"

        instance_join = ""
        if parameter in ("int", "sta"):
            assembly_instance = "%s_instance" % parameter
            instance_join = (
                "JOIN %(assembly_instance)s i " "ON i.id = assembly.instance_id"
            )
            instance_join = self.env.cr.mogrify(
                instance_join, {"assembly_instance": AsIs(assembly_instance)}
            )
            instance_join = instance_join.decode("utf-8")
        assembly_type = "%s_assembly" % parameter
        assembly_category = "%s_assembly_category" % parameter
        values.update(
            {
                "model_name": "%s.assembly" % parameter,
                "int_instance_id": AsIs(int_instance_id),
                "int_cat_id": AsIs(int_cat_id),
                "sta_cat_id": AsIs(sta_cat_id),
                "ext_cat_id": AsIs(ext_cat_id),
                "int_power_id": AsIs(int_power_id),
                "sta_power_id": AsIs(sta_power_id),
                "assembly_type": AsIs(assembly_type),
                "assembly_category": AsIs(assembly_category),
                "instance_join": AsIs(instance_join),
            }
        )
        return values

    @api.model
    def _get_select(self):
        select = (
            super()._get_select()
            + """,
            %(model_name)s as model,
            cat.name as category,
            p.int_instance_id,
            %(int_cat_id)s as int_category_assembly_id,
            %(sta_cat_id)s as sta_category_assembly_id,
            %(ext_cat_id)s as ext_category_assembly_id,
            %(int_power_id)s as int_power_level_id,
            %(sta_power_id)s as sta_power_level_id"""
        )
        return select

    @api.model
    def _get_from(self):
        from_query = """
            FROM %(assembly_type)s assembly
            JOIN res_partner AS p
                ON p.id = assembly.partner_id
            JOIN %(assembly_category)s AS cat
                ON cat.id = assembly.assembly_category_id
            %(instance_join)s"""
        return from_query

    @api.model
    def _get_where(self):
        where = "WHERE assembly.active = TRUE AND p.active = TRUE"
        return where
