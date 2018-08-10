# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import api, models, fields
from odoo.tests.common import TransactionCase
from odoo.fields import first

_logger = logging.getLogger(__name__)


class TestAbstractCoordinate(models.Model):
    """
    A concrete Odoo model used for these tests only
    """
    _description = 'Test abstract coordinate'
    _name = 'test.abstract.coordinate'
    _inherit = ['abstract.coordinate']
    _abstract = True

    _discriminant_field = 'discr_field'
    _unicity_keys = 'id'

    name = fields.Char()
    discr_field = fields.Char()


class TestResPartner(models.Model):
    """
    Add an inverse on res.partner related to the concrete model created
    just before.
    Also, add a computed field to know which one is the main.
    """
    _name = 'res.partner'
    _inherit = 'res.partner'

    not_abstract_coordinate_id = fields.Many2one(
        TestAbstractCoordinate._name,
        "A test field",
        compute='_compute_not_abstract_coordinate_id',
    )
    not_abstract_coordinate_ids = fields.One2many(
        TestAbstractCoordinate._name,
        'partner_id',
        "A test field",
    )

    @api.multi
    @api.depends('not_abstract_coordinate_ids')
    def _compute_not_abstract_coordinate_id(self):
        """
        Compute function to have the coordinate when is_main is True
        for current partners
        :return:
        """
        coord_obj = self.env[TestAbstractCoordinate._name].sudo()
        coordinates = coord_obj.search([
            ('partner_id', 'in', self.ids),
            ('is_main', '=', True),
            ('active', '=', True),
        ])
        for record in self:
            coordinate = coordinates.filtered(
                lambda c, r=record: c.partner_id.id == r.id and c.is_main)
            coordinate = first(coordinate.with_prefetch(self._prefetch))
            record.not_abstract_coordinate_id = coordinate

    @api.multi
    def _compute_commercial_partner(self):
        """
        Just overwrite this function to avoid useless crash of unit test
        :return:
        """
        for partner in self:
            partner.commercial_partner_id = self.env['res.partner'].browse()


class TestCommonAbstractCoordinate(TransactionCase):
    """
    Common class who instantiate some models (given by _get_odoo_models())
    used for current tests
    """

    def _get_odoo_models(self):
        """
        Get Odoo Models to instantiate for current tests
        :return: list of Odoo Models
        """
        return [TestAbstractCoordinate, TestResPartner]

    def _init_test_models(self):
        """
        Function to init/create a new Odoo Model during unit test.
        :return: instance of model (empty)
        """
        models_cls = self._get_odoo_models()
        registry = self.env.registry
        cr = self.env.cr
        for model_cls in models_cls:
            model_cls._build_model(registry, cr)
        registry.setup_models(cr)
        names = [m._name for m in models_cls]
        registry.init_models(cr, names, self.env.context)
        return True

    def setUp(self):
        super().setUp()
        registry = self.registry
        # We must be in test mode before create/init new models
        registry.enter_test_mode()
        # Add the cleanup to disable test mode after this setup as finished
        self.addCleanup(registry.leave_test_mode)
        self._init_test_models()
        self.model_coordinate = self.env[TestAbstractCoordinate._name]
        # Use the inverse field set on the res.partner
        self.coo_into_partner = 'not_abstract_coordinate_id'
