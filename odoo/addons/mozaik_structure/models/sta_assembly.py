# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StaAssembly(models.Model):

    _name = 'sta.assembly'
    _inherit = ['abstract.assembly']
    _description = 'State Assembly'

    assembly_category_id = fields.Many2one(
        comodel_name='sta.assembly.category',
    )
    instance_id = fields.Many2one(
        comodel_name='sta.instance',
    )
    is_legislative = fields.Boolean(
        related='assembly_category_id.is_legislative',
        readonly=True,
        store=True,
    )
    electoral_district_ids = fields.One2many(
        'electoral.district',
        'assembly_id',
        string='Electoral Districts',
        domain=[('active', '<=', True)],
    )

    @api.model
    def _get_names(self, vals=None):
        '''
        Get the tuple of names needed to build the assembly name
        :param values: dict
        :return: tuple of string
        '''
        n1 = (
            self and self.instance_id or
            vals and self.env['sta.instance'].browse(
                vals.get('instance_id')).name or
            False
        )
        n2 = (
            self and self.assembly_category_id or
            vals and self.env['sta.assembly.category'].browse(
                vals.get('assembly_category_id')).name or
            False
        )
        return (n1, n2)
