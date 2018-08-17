# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ElectoralDistrict(models.Model):

    _name = 'electoral.district'
    _inherit = ['mozaik.abstract.model']
    _description = 'Electoral District'
    _order = 'name'
    _unicity_keys = 'sta_instance_id, assembly_id'

    name = fields.Char(
        required=True,
        index=True,
        track_visibility='onchange',
    )
    sta_instance_id = fields.Many2one(
        'sta.instance',
        string='State Instance',
        required=True,
        index=True,
        track_visibility='onchange',
    )
    int_instance_id = fields.Many2one(
        'int.instance',
        string='Internal Instance',
        index=True,
        readonly=True,
        related='sta_instance_id.int_instance_id',
        store=True,
    )
    assembly_id = fields.Many2one(
        'sta.assembly',
        string='Assembly',
        required=True,
        index=True,
        track_visibility='onchange',
        domain=[('is_legislative', '=', True)],
    )
    power_level_id = fields.Many2one(
        'sta.power.level',
        string='Power Level',
        readonly=True,
        related='assembly_id.assembly_category_id.power_level_id',
    )
    designation_int_assembly_id = fields.Many2one(
        'int.assembly',
        string='Designation Assembly',
        index=True,
        track_visibility='onchange',
        domain=[('is_designation_assembly', '=', True)],
    )
    assembly_category_id = fields.Many2one(
        'sta.assembly.category',
        string='State Assembly Category',
        readonly=True,
        related='assembly_id.assembly_category_id',
    )

    _sql_constraints = [
        ('unique_name', 'UNIQUE ( name )', 'The name must be unique.'),
    ]

    @api.model
    def create(self, values):
        """
        Provide a name if any
        """
        if not values.get('name'):
            values['name'] = self.env['sta.instance'].browse(
                values.get('instance_id')).name or False
        res = super().create(values)
        return res

    @api.onchange('sta_instance_id')
    def _onchange_sta_instance_id(self):
        self.ensure_one()
        if self.sta_instance_id:
            self.name = self.sta_instance_id.name_get()[0][1]
            if self.sta_instance_id.int_instance_id:
                self.int_instance_id = self.sta_instance_id.int_instance_id

    @api.onchange('assembly_id')
    def _onchange_assembly_id(self):
        self.ensure_one()
        if self.assembly_id and self.assembly_id.designation_int_assembly_id:
            self.designation_int_assembly_id = \
                self.assembly_id.designation_int_assembly_id
