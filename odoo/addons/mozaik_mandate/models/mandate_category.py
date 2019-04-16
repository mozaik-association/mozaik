# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

# Constants
MANDATE_CATEGORY_AVAILABLE_TYPES = [
    ('sta', 'State'),
    ('int', 'Internal'),
    ('ext', 'External'),
]

mandate_category_available_types = dict(MANDATE_CATEGORY_AVAILABLE_TYPES)


class MandateCategory(models.Model):
    _name = 'mandate.category'
    _description = 'Mandate Category'
    _inherit = ['mozaik.abstract.model']
    _order = 'name'

    _unicity_keys = 'type, name'

    _sql_constraints = [
        ('ref_categ_check',
         'CHECK(sta_assembly_category_id+int_assembly_category_id+'
         'ext_assembly_category_id > 0)',
         'An Assembly Category is required.'),
    ]

    name = fields.Char(
        required=True,
        index=True,
        track_visibility='onchange')
    type = fields.Selection(
        selection=MANDATE_CATEGORY_AVAILABLE_TYPES,
        index=True,
        required=True)
    exclusive_category_m2m_ids = fields.Many2many(
        comodel_name='mandate.category',
        relation='mandate_category_mandate_category_rel',
        column1='id',
        column2='exclu_id',
        string='Exclusive Category')
    sta_assembly_category_id = fields.Many2one(
        comodel_name='sta.assembly.category',
        string='State Assembly Category',
        track_visibility='onchange')
    ext_assembly_category_id = fields.Many2one(
        comodel_name='ext.assembly.category',
        string='External Assembly Category',
        track_visibility='onchange')
    int_assembly_category_id = fields.Many2one(
        comodel_name='int.assembly.category',
        string='Internal Assembly Category',
        track_visibility='onchange')
    sta_mandate_ids = fields.One2many(
        comodel_name='sta.mandate',
        inverse_name='mandate_category_id',
        string='State Mandates')
    int_mandate_ids = fields.One2many(
        comodel_name='int.mandate',
        inverse_name='mandate_category_id',
        string='Internal Mandates')
    ext_mandate_ids = fields.One2many(
        comodel_name='ext.mandate',
        inverse_name='mandate_category_id',
        string='External Mandates')
    with_revenue_declaration = fields.Boolean(
        help='Submission to a Mandates and Wages Declaration',
        oldname="is_submission_mandate")
    with_assets_declaration = fields.Boolean(
        help='Submission to a Mandates and Assets Declaration',
        oldname="is_submission_assets")

    @api.multi
    def copy_data(self, default=None):
        res = super().copy_data(default=default)

        res[0].update({
            'name': _('%s (copy)') % res[0].get('name'),
        })
        return res

    @api.model
    def create(self, vals):
        res_id = super().create(vals)
        if 'exclusive_category_m2m_ids' in vals:
            res_id._check_exclusive_consistency(
                [], vals['exclusive_category_m2m_ids'])
        return res_id

    @api.multi
    def write(self, vals):
        if 'exclusive_category_m2m_ids' in vals:
            for category in self:
                cat_ids = [record.id
                           for record in category.exclusive_category_m2m_ids]
                category._check_exclusive_consistency(
                    cat_ids, vals['exclusive_category_m2m_ids'])

        res = super().write(vals)
        return res

    @api.multi
    def _check_exclusive_consistency(
            self, initial_exclu_ids, magic_categories):
        """
        Check balance between exclusive categories
        :rparam: mandate_category ids, list of initial exclusive ids,
                 list of new exclusive ids
        :rtype: Boolean
        """
        new_exclu_ids = []
        if magic_categories[0][0] == 6:
            new_exclu_ids = magic_categories[0][2]
        if magic_categories[0][0] == 4:
            new_exclu_ids = [c[1] for c in magic_categories]
            new_exclu_ids += initial_exclu_ids

        removed_ids = list(set(initial_exclu_ids) - set(new_exclu_ids))
        added_ids = list(set(new_exclu_ids) - set(initial_exclu_ids))

        if removed_ids:
            # category are not exclusives anymore
            self._impact_related_exclusive_category(
                removed_ids, 'in',)
        if added_ids:
            # category are exclusives from now
            self._impact_related_exclusive_category(
                added_ids, 'not in', exclu_ids=self.ids)

        return True

    @api.multi
    def _impact_related_exclusive_category(
            self, linked_ids, operator, exclu_ids=None):
        """
        ==============================
        _impact_related_exclusive_category
        ==============================
        Impact relative categories to add or remove a link to current id
        """
        exclu_ids = exclu_ids or []
        for exclu in self.search(
                [('id', 'in', linked_ids),
                 ('exclusive_category_m2m_ids', operator, self.ids)]):
            exclu_ids.extend([exclu_id.id for exclu_id in
                              exclu.exclusive_category_m2m_ids
                              if exclu_id not in self])
            vals = dict(exclusive_category_m2m_ids=[[6, False, exclu_ids]])
            # super to avoid cyclic call to write
            super(MandateCategory, exclu).write(vals)
        return True
