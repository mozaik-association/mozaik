# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _


class AbstractAssembly(models.AbstractModel):

    _name = 'abstract.assembly'
    _inherit = ['mozaik.abstract.model']
    _description = 'Abstract Assembly'
    _order = 'partner_id, assembly_category_id'
    _unicity_keys = 'instance_id, assembly_category_id'
    _log_access = True

    assembly_category_id = fields.Many2one(
        'abstract.assembly.category',
        string='Category',
        index=True,
        required=True,
        track_visibility='onchange',
    )
    instance_id = fields.Many2one(
        'abstract.instance',
        string='Instance',
        index=True,
        required=True,
        track_visibility='onchange',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Related Partner',
        index=True,
        required=True,
        readonly=True,
        ondelete='restrict',
        auto_join=True,
        delegate=True,
    )
    designation_int_assembly_id = fields.Many2one(
        'int.assembly',
        string='Designation Assembly',
        index=True,
        track_visibility='onchange',
        domain=[('is_designation_assembly', '=', True)],
    )
    months_before_end_of_mandate = fields.Integer(
        'Alert Delay (#Months)',
        track_visibility='onchange',
        group_operator='min',
    )

    @api.multi
    @api.constrains('instance_id', 'assembly_category_id')
    def _check_power_level(self):
        """
        Check if power levels of assembly category and instance are
        consistents.
        Note:
        Only relevant for internal and state assemblies
        """
        for assembly in self:
            if assembly.assembly_category_id.power_level_id !=\
                    assembly.instance_id.power_level_id:
                raise exceptions.ValidationError(
                    _('Power level of category and instance are inconsistent'))

    @api.model
    def _get_names(self, vals=None):
        '''
        Intended to be inherited
        :param values: dict
        :return: tuple
        '''
        return (False, False)

    @api.model
    def _build_name(self, names):
        '''
        Build the name of the related partner
        :param values: tuple of string
        :return: string
        '''
        name = '%s (%s)' % names
        return name

    @api.model
    def create(self, values):
        """
        Force is_assembly and is_company
        Provide a name if any
        """
        values.update({
            'is_company': True,
            'is_assembly': True,
        })
        if not values.get('name') and not values.get('partner_id'):
            values['name'] = self._build_name(self._get_names(vals=values))
        res = super().create(values)
        return res

    @api.multi
    def unlink(self):
        """
        Reset is_assembly of related partners
        """
        partners = self.mapped('partner_id')
        res = super().unlink()
        partners.write({'is_assembly': False})
        return res

    @api.onchange(
        'instance_id', 'assembly_category_id')
    def _onchange_assembly_category_or_instance(self):
        '''
        Rebuid assembly name when changing its instance or its category
        '''
        self.ensure_one()
        if self.instance_id and self.assembly_category_id:
            self.name = self._build_name(self._get_names())

    @api.onchange('assembly_category_id')
    def _onchange_assembly_category_id(self):
        self.ensure_one()
        if self.assembly_category_id:
            self.months_before_end_of_mandate = \
                self.assembly_category_id.months_before_end_of_mandate
