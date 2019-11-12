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

    model = fields.Char(
        string='Models')
    mandate_id = fields.Integer(
        string='Mandate ID',
        group_operator='min')
    mandate_ref = fields.Char(
        string='Mandate Reference')
    mandate_category_id = fields.Many2one(
        comodel_name='mandate.category',
        string='Exclusive Categories')
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
        partner.name as assembly_name
        """

    def _select_int_mandate(self):
        return """
        'int.mandate' AS model,
        concat('int.mandate,', mandate.id) as mandate_ref,""" + \
            self._select_mandate()

    def _select_ext_mandate(self):
        return """
        'ext.mandate' AS model,
        concat('ext.mandate,', mandate.id),""" + self._select_mandate()

    def _select_sta_mandate(self):
        return """
        'sta.mandate' AS model,
        concat('sta.mandate,', mandate.id),""" + self._select_mandate()

    def init(self):
        tools.drop_view_if_exists(self._cr, 'generic_mandate')
        self.env.cr.execute("""
            create or replace view generic_mandate as (
                SELECT %(select_int_mandate)s
                    FROM int_mandate  AS mandate
                    JOIN int_assembly AS assembly
                      ON assembly.id = mandate.int_assembly_id
                    JOIN res_partner  AS partner
                      ON partner.id = assembly.partner_id
                    WHERE mandate.active = True
                    AND mandate.end_date is NULL

                UNION

                SELECT %(select_sta_mandate)s
                    FROM sta_mandate  AS mandate
                    JOIN sta_assembly AS assembly
                      ON assembly.id = mandate.sta_assembly_id
                    JOIN res_partner  AS partner
                      ON partner.id = assembly.partner_id
                    WHERE mandate.active = True
                    AND mandate.end_date is NULL

                UNION

                SELECT %(select_ext_mandate)s
                    FROM ext_mandate  AS mandate
                    JOIN ext_assembly AS assembly
                      ON assembly.id = mandate.ext_assembly_id
                    JOIN res_partner  AS partner
                      ON partner.id = assembly.partner_id
                    WHERE mandate.active = True
                    AND mandate.end_date is NULL
            )
            """, {
            "select_int_mandate": AsIs(self._select_int_mandate()),
            "select_sta_mandate": AsIs(self._select_sta_mandate()),
            "select_ext_mandate": AsIs(self._select_ext_mandate()),
        })

    @api.multi
    def name_get(self):
        res = []
        for mandate in self:
            display_name = '{name} ({mandate_category})'.format(
                name=mandate.partner_id.name,
                mandate_category=mandate.mandate_category_id.name)
            res.append((mandate.id, display_name))
        return res

    @api.multi
    def button_view_mandate(self):
        """
        View mandates in its form view depending on model
        """
        self.ensure_one()
        return self.env[self.model].browse(
            self.mandate_id).get_formview_action()
