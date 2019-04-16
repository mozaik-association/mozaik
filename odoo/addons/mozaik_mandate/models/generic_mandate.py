# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


def _get_document_types(s):
    s.env.cr.execute("SELECT model, name from ir_model WHERE model IN \
                ('sta.mandate', 'int.mandate', 'ext.mandate') ORDER BY name")
    return s.env.cr.fetchall()


class GenericMandate(models.Model):
    _name = "generic.mandate"
    _description = 'Generic Mandate'
    _auto = False
    _rec_name = 'mandate_ref'
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
        model, m_id = self.mandate_ref.split(',')
        return self.env[self.model].browse(int(m_id))\
            ._get_discriminant_value(force_field=force_field)

    def _is_discriminant_m2o(self):
        return isinstance(self._columns[self._discriminant_field],
                          fields.Many2one)

    model = fields.Char(
        string='Models')
    mandate_id = fields.Integer(
        string='Mandate ID',
        group_operator='min')
    mandate_ref = fields.Selection(
        string='Mandate Reference',
        selection=_get_document_types)
    mandate_category_id = fields.Many2one(
        comodel_name='mandate.category',
        string='Mandate Category')
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

    def init(self):
        self.env.cr.execute("""
            create or replace view generic_mandate as (
                    SELECT 'int.mandate' AS model,
                           mandate.unique_id as id,
                           mandate.id as mandate_id,
                           concat('int.mandate,', mandate.id) as mandate_ref,
                           mandate.mandate_category_id,
                           mandate.partner_id,
                           mandate.start_date,
                           mandate.deadline_date,
                           mandate.is_duplicate_detected,
                           mandate.is_duplicate_allowed,
                           partner.name as assembly_name
                        FROM int_mandate  AS mandate
                        JOIN int_assembly AS assembly
                          ON assembly.id = mandate.int_assembly_id
                        JOIN res_partner  AS partner
                          ON partner.id = assembly.partner_id
                        WHERE mandate.active = True
                        AND mandate.end_date is NULL

                    UNION

                    SELECT 'sta.mandate' AS model,
                           mandate.unique_id as id,
                           mandate.id as mandate_id,
                           concat('sta.mandate,', mandate.id),
                           mandate.mandate_category_id,
                           mandate.partner_id,
                           mandate.start_date,
                           mandate.deadline_date,
                           mandate.is_duplicate_detected,
                           mandate.is_duplicate_allowed,
                           partner.name as assembly_name
                        FROM sta_mandate  AS mandate
                        JOIN sta_assembly AS assembly
                          ON assembly.id = mandate.sta_assembly_id
                        JOIN res_partner  AS partner
                          ON partner.id = assembly.partner_id
                        WHERE mandate.active = True
                        AND mandate.end_date is NULL

                    UNION

                    SELECT 'ext.mandate' AS model,
                           mandate.unique_id as id,
                           mandate.id as mandate_id,
                           concat('ext.mandate,', mandate.id),
                           mandate.mandate_category_id,
                           mandate.partner_id,
                           mandate.start_date,
                           mandate.deadline_date,
                           mandate.is_duplicate_detected,
                           mandate.is_duplicate_allowed,
                           partner.name as assembly_name
                        FROM ext_mandate  AS mandate
                        JOIN ext_assembly AS assembly
                          ON assembly.id = mandate.ext_assembly_id
                        JOIN res_partner  AS partner
                          ON partner.id = assembly.partner_id
                        WHERE mandate.active = True
                        AND mandate.end_date is NULL
                )
            """)

    @api.multi
    def button_view_mandate(self):
        """
        View mandates in its form view depending on model
        """
        self.ensure_one()
        model, m_id = self.mandate_ref.split(',')
        return self.env[self.model].browse(int(m_id)).get_formview_action()
