# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _


class StaInstance(models.Model):

    _name = 'sta.instance'
    _inherit = ['abstract.instance']
    _description = 'State Instance'

    parent_id = fields.Many2one(
        comodel_name='sta.instance',
    )
    power_level_id = fields.Many2one(
        comodel_name='sta.power.level',
        required=True,
    )
    assembly_ids = fields.One2many(
        comodel_name='sta.assembly',
    )
    assembly_inactive_ids = fields.One2many(
        comodel_name='sta.assembly',
    )
    electoral_district_ids = fields.One2many(
        'electoral.district',
        'int_instance_id',
        string='Electoral Districts',
        domain=[('active', '=', True)],
    )
    electoral_district_inactive_ids = fields.One2many(
        'electoral.district',
        'int_instance_id',
        string='Electoral Districts',
        domain=[('active', '=', False)],
    )
    secondary_parent_id = fields.Many2one(
        'sta.instance',
        string='Secondary Parent Instance',
        index=True,
        track_visibility='onchange',
    )
    int_instance_id = fields.Many2one(
        'int.instance',
        string='Internal Instance',
        index=True,
        track_visibility='onchange',
        default=lambda s: s._get_default_int_instance_id(),
    )
    identifier = fields.Char(
        'External Identifier (INS)',
        track_visibility='onchange',
    )

    _sql_constraints = [
        ('unique_identifier', 'UNIQUE ( identifier )',
         'The external identifier (INS) must be unique.'),
    ]

    def _get_default_int_instance_id(self):
        return self.env['int.instance']._get_default_int_instance()

    @api.multi
    @api.constrains('secondary_parent_id')
    def _check_secondary_instance_recursion(self):
        """
        Check for recursion in instances hierarchy
        """
        if not self._check_recursion('secondary_parent_id'):
            raise exceptions.ValidationError(
                _('You can not create recursive instances'))
