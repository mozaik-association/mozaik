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

    _unicity_keys = 'type, assembly_categoryid, name'

    _sql_constraints = [
        ('ref_categ_check',
         'CHECK('
         '(sta_assembly_category_id>0 and '
         ' int_assembly_category_id is null and '
         ' ext_assembly_category_id is null)'
         ' OR '
         '(int_assembly_category_id>0 and '
         ' sta_assembly_category_id is null and '
         ' ext_assembly_category_id is null)'
         ' OR '
         '(ext_assembly_category_id>0 and '
         ' int_assembly_category_id is null and '
         ' sta_assembly_category_id is null)'
         ')',
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
    assembly_categoryid = fields.Integer(
        string='Assembly category',
        compute='_compute_assembly_categoryid',
        store=True,
        required=True,
        # to avoid null for required=True
        default=0,
    )
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
        help='Representative is subject to a declaration of income',
        oldname="is_submission_mandate")
    with_assets_declaration = fields.Boolean(
        help='Representative is subject to a declaration of assets',
        oldname="is_submission_assets")

    @api.multi
    @api.depends(
        'sta_assembly_category_id', 'int_assembly_category_id',
        'ext_assembly_category_id')
    def _compute_assembly_categoryid(self):
        """
        Compute pseudo assembly category m2o for unicity key
        """
        for record in self:
            record.assembly_categoryid = (
                record.sta_assembly_category_id.id or
                record.int_assembly_category_id.id or
                record.ext_assembly_category_id.id or 0)

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
            res_id._update_exclusive_inverse_relation(
                self, res_id.exclusive_category_m2m_ids)
        return res_id

    @api.multi
    def write(self, vals):
        res = True
        if 'exclusive_category_m2m_ids' in vals:
            for category in self:
                cat_before = category.exclusive_category_m2m_ids
                res = res and super().write(vals)
                cat_after = category.exclusive_category_m2m_ids
                category._update_exclusive_inverse_relation(
                    cat_before, cat_after)
        else:
            res = super().write(vals)
        return res

    @api.multi
    def _update_exclusive_inverse_relation(self, initial_exclu, after_exclu):
        """
        Check balance between exclusive categories
        :rparam: mandate_category ids, list of initial exclusive ids,
                 list of new exclusive ids
        :rtype: Boolean
        """
        self.ensure_one()
        removed_ids = initial_exclu - after_exclu
        added_ids = after_exclu - initial_exclu

        res = True
        if removed_ids:
            # category are not exclusives anymore
            # super to avoid cyclic call to write
            res = res and super(MandateCategory, removed_ids).write({
                "exclusive_category_m2m_ids": [(3, self.id)]
            })
        if added_ids:
            # category are exclusives from now
            # super to avoid cyclic call to write
            res = res and super(MandateCategory, added_ids).write({
                "exclusive_category_m2m_ids": [(4, self.id)]
            })
        return res
