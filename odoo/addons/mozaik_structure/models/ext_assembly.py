# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _


class ExtAssembly(models.Model):

    _name = 'ext.assembly'
    _inherit = ['abstract.assembly']
    _description = "External Assembly"
    _unicity_keys = 'ref_partner_id, assembly_category_id'

    assembly_category_id = fields.Many2one(
        comodel_name='ext.assembly.category',
    )
    instance_id = fields.Many2one(
        comodel_name='int.instance',
        default=lambda s: s._get_default_instance(),
    )
    ref_partner_id = fields.Many2one(
        'res.partner',
        string='Legal Person',
        index=True,
        required=True,
        ondelete='restrict',
        track_visibility='onchange',
        context={
            'default_is_company': True,
        },
        domain=[('is_company', '=', True), ('is_assembly', '=', False)],
    )

    def _get_default_instance_id(self):
        return self.env['int.instance']._get_default_int_instance()

    @api.multi
    def _check_power_level(self):
        """
        Not relevant for external assembly
        """
        pass

    @api.multi
    @api.constrains('ref_partner_id')
    def _check_ref_partner_id(self):
        """
        Check if ref partner is a company and not an assembly
        """
        for assembly in self:
            if not assembly.ref_partner_id.is_company:
                raise exceptions.ValidationError(
                    _('Reference partner must be a company'))
            if assembly.ref_partner_id.is_assembly:
                raise exceptions.ValidationError(
                    _('Reference partner cannot be an assembly'))

    @api.model
    def _get_names(self, vals=None):
        '''
        Get the tuple of names needed to build the assembly name
        :param values: dict
        :return: tuple of string
        '''
        n1 = (
            self and self.ref_partner_id or
            vals and self.env['res.partner'].browse(
                vals.get('ref_partner_id')).name or
            False
        )
        n2 = (
            self and self.assembly_category_id or
            vals and self.env['ext.assembly.category'].browse(
                vals.get('assembly_category_id')).name or
            False
        )
        return (n1, n2)

    @api.onchange(
        'ref_partner_id', 'assembly_category_id')
    def _onchange_assembly_category_or_instance(self):
        '''
        Rebuid assembly name when changing its partner or its category
        Rewriting without calling super()
        '''
        self.ensure_one()
        if self.ref_partner_id and self.assembly_category_id:
            self.name = self._build_name(self._get_names())
