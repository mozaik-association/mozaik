# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import api, exceptions, fields, models, _
from odoo.fields import first

_logger = logging.getLogger(__name__)


class IntInstance(models.Model):
    _name = 'int.instance'
    _inherit = ['abstract.instance']
    _description = 'Internal Instance'

    parent_id = fields.Many2one(
        comodel_name='int.instance',
    )
    power_level_id = fields.Many2one(
        comodel_name='int.power.level',
        required=True,
    )
    assembly_ids = fields.One2many(
        comodel_name='int.assembly',
    )
    assembly_inactive_ids = fields.One2many(
        comodel_name='int.assembly',
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
    multi_instance_pc_ids = fields.Many2many(
        'int.instance',
        'int_instance_int_instance_rel',
        column1='id',
        column2='child_id',
        string='Multi-Instances',
        domain=[('active', '<=', True)],
        oldname='multi_instance_pc_m2m_ids',
    )
    multi_instance_cp_ids = fields.Many2many(
        'int.instance',
        'int_instance_int_instance_rel',
        column1='child_id',
        column2='id',
        string='Multi-Instances',
        domain=[('active', '<=', True)],
        oldname='multi_instance_cp_m2m_ids',
    )
    code = fields.Char(
        copy=False,
    )

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Instance code must be unique'),
    ]

    @api.multi
    @api.constrains('code')
    def _check_code_size(self):
        """
        Check if the code has the correct size and is digit
        :return:
        """
        size = int(self.env['ir.config_parameter'].sudo().get_param(
            'structure.instance_code_size', default=3))
        # If size is not equals to size in parameters or value is not digit
        bad_instances = self.filtered(
            lambda l: len(l.code or '') != size or not l.code.isdigit())
        if bad_instances:
            details = "\n- ".join(bad_instances.mapped("code"))
            message = _("These instance codes are not valid:\n- %s") % details
            raise exceptions.ValidationError(message)

    @api.model
    def _get_default_int_instance(self):
        """
        Get the default Internal Power Level
        """
        res_id = self.env.ref('mozaik_structure.int_instance_01')
        return res_id

    @api.multi
    def _get_secretariat(self):
        '''
        Get the secretariat related to the given instance
        '''
        self.ensure_one()
        secretariats = self.assembly_ids.filtered(
            lambda s: s.is_secretariat)
        if not secretariats:
            _logger.info(
                'No secretariat found for internal instance %s',
                self.name)
        return first(secretariats)

    @api.multi
    def _get_instance_followers(self):
        '''
        Get related partners of all secretariats associated to self
        '''
        self_sudo = self.sudo()
        instances = self_sudo.browse()
        while self_sudo:
            instances |= self_sudo
            self_sudo = self_sudo.mapped('parent_id')

        assemblies = instances.mapped('assembly_ids')
        assemblies = assemblies.filtered(
            lambda s: s.is_secretariat and
            s.instance_id.power_level_id.level_for_followers)
        partners = assemblies.mapped('partner_id')
        return partners
