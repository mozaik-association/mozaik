# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _


class AbstractInstance(models.AbstractModel):

    _name = 'abstract.instance'
    _inherit = ['mozaik.abstract.model']
    _description = 'Abstract Instance'
    _parent_name = 'parent_id'
    _parent_store = True
    _parent_order = 'name'
    _order = 'name'
    _unicity_keys = 'power_level_id, name'
    _log_access = True

    name = fields.Char(
        required=True,
        index=True,
        tracking=True,
    )
    power_level_id = fields.Many2one(
        'abstract.power.level',
        string='Power Level',
        required=True,
        index=True,
        tracking=True,
    )
    parent_id = fields.Many2one(
        'abstract.instance',
        string='Parent Instance',
        index=True,
        ondelete='restrict',
        tracking=True,
    )
    parent_path = fields.Char(index=True)
    assembly_ids = fields.One2many(
        'abstract.assembly',
        'instance_id',
        string='Assemblies',
        domain=[('active', '=', True)],
    )
    assembly_inactive_ids = fields.One2many(
        'abstract.assembly',
        'instance_id',
        string='Assemblies (Inactive)',
        domain=[('active', '=', False)],
    )

    @api.constrains('power_level_id')
    def _check_power_level(self):
        """
        Check if power level is consistent with all related assembly
        Note:
        Only relevant for internal and state assemblies
        """
        for instance in self:
            assemblies = instance.assembly_ids + instance.assembly_inactive_ids
            power_levels = (
                assemblies.mapped('assembly_category_id.power_level_id') -
                instance.power_level_id)
            if power_levels:
                raise exceptions.ValidationError(
                    _('Power level is inconsistent with '
                      'power level of all related assemblies'))

    @api.depends('name', 'power_level_id', 'power_level_id.name')
    def name_get(self):
        result = []
        for instance in self:
            name = '%s (%s)' % (instance.name, instance.power_level_id.name)
            result.append((instance.id, name))
        return result
