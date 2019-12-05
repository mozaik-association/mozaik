# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs
from odoo import api, fields, models, tools


class GenericMandate(models.Model):
    _name = "generic.mandate"
    _description = 'Generic Mandate'
    _auto = False
    _order = 'partner_id, mandate_category_id'

    _discriminant_field = 'partner_id'

    @api.multi
    def _get_discriminant_value(self, force_field=False):
        """
        Get the value of the discriminant field
        :param force_field: str
        :return: str, int, float, bool
        """
        self.ensure_one()
        return self.env[self.model].browse(self.mandate_id)\
            ._get_discriminant_value(force_field=force_field)

    def _is_discriminant_m2o(self):
        return isinstance(self._columns[self._discriminant_field],
                          fields.Many2one)

    @api.multi
    @api.depends("partner_id", "mandate_category_id")
    def _compute_name(self):
        for mandate in self:
            mandate.name = "%s (%s)" % (
                mandate.partner_id.display_name,
                mandate.mandate_category_id.display_name,
            )

    name = fields.Char(compute="_compute_name")
    model = fields.Char(
        string='Models')
    mandate_id = fields.Integer(
        string='Mandate ID',
        group_operator='min')
    mandate_category_id = fields.Many2one(
        comodel_name='mandate.category')
    assembly_name = fields.Char(
        string="Assembly")
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Representative')
    start_date = fields.Date()
    deadline_date = fields.Date()
    is_duplicate_detected = fields.Boolean(
        string='Incompatible Mandate')
    is_duplicate_allowed = fields.Boolean(
        string='Allowed Incompatible Mandate')
    with_remuneration = fields.Boolean()

    def _select_mandate(self):
        return """
        mandate.unique_id as id,
        mandate.id as mandate_id,
        mandate.mandate_category_id,
        mandate.partner_id,
        mandate.start_date,
        mandate.deadline_date,
        mandate.is_duplicate_detected,
        mandate.is_duplicate_allowed,
        mandate.with_remuneration as with_remuneration,
        partner.name as assembly_name
        """

    def _join_mandate(self):
        return """
        JOIN res_partner AS partner
          ON partner.id = assembly.partner_id"""

    def _select_int_mandate(self):
        return "'int.mandate' AS model, " + self._select_mandate()

    def _join_int_mandate(self):
        return """
        JOIN int_assembly AS assembly
          ON assembly.id = mandate.int_assembly_id""" + self._join_mandate()

    def _select_ext_mandate(self):
        return "'ext.mandate' AS model, " + self._select_mandate()

    def _join_ext_mandate(self):
        return """
        JOIN ext_assembly AS assembly
          ON assembly.id = mandate.ext_assembly_id""" + self._join_mandate()

    def _select_sta_mandate(self):
        return "'sta.mandate' AS model, " + self._select_mandate()

    def _join_sta_mandate(self):
        return """
        JOIN sta_assembly AS assembly
          ON assembly.id = mandate.sta_assembly_id""" + self._join_mandate()

    def init(self):
        tools.drop_view_if_exists(self._cr, 'generic_mandate')
        self.env.cr.execute("""
            create or replace view generic_mandate as (
                SELECT %(select_int_mandate)s
                    FROM int_mandate  AS mandate
                    %(join_int_mandate)s
                    WHERE mandate.active = True
                    AND mandate.end_date is NULL

                UNION

                SELECT %(select_sta_mandate)s
                    FROM sta_mandate  AS mandate
                    %(join_sta_mandate)s
                    WHERE mandate.active = True
                    AND mandate.end_date is NULL

                UNION

                SELECT %(select_ext_mandate)s
                    FROM ext_mandate  AS mandate
                    %(join_ext_mandate)s
                    WHERE mandate.active = True
                    AND mandate.end_date is NULL
            )
            """, {
            "select_int_mandate": AsIs(self._select_int_mandate()),
            "join_int_mandate": AsIs(self._join_int_mandate()),
            "select_sta_mandate": AsIs(self._select_sta_mandate()),
            "join_sta_mandate": AsIs(self._join_sta_mandate()),
            "select_ext_mandate": AsIs(self._select_ext_mandate()),
            "join_ext_mandate": AsIs(self._join_ext_mandate()),
        })

    @api.multi
    def button_view_mandate(self):
        """
        View mandates in its form view depending on model
        """
        self.ensure_one()
        return self.env[self.model].browse(
            self.mandate_id).get_formview_action()
