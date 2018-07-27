# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from uuid import uuid4
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError
from .common import CommonCoordinate

_logger = logging.getLogger(__name__)


class CommonAbstractCoordinate(CommonCoordinate):
    """
    Test for abstract.coordinate
    This class have some abstract test to check with concrete models
    """

    def setUp(self):
        super(CommonAbstractCoordinate, self).setUp()
        self.partner_obj = self.env['res.partner']
        self.partner1 = self.env.ref("mozaik_coordinate.res_partner_thierry")
        self.partner2 = self.env.ref("mozaik_coordinate.res_partner_pauline")
        self.partner3 = self.env.ref("mozaik_coordinate.res_partner_nicolas")
        # Use unique values
        self.field_id_1 = str(uuid4())
        self.field_id_2 = str(uuid4())
        self.field_id_3 = str(uuid4())

    def test_unicity_of_abstract_coordinate(self):
        """
        Test the fact that the model coordinate must be unique with
        partner_id, model_id when no expire date
        """
        values = {
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
            'is_main': True,
        }
        self.model_coordinate.create(values)
        values.update({
            'is_main': False,
        })
        # Disable error into logs
        self.env.cr._default_log_exceptions = False
        with self.assertRaises(IntegrityError):
            self.model_coordinate.create(values)
        self.env.cr._default_log_exceptions = True
        return

    def test_create_new_main(self):
        """
        Test the fact that a created model coordinate that is main selected
        will set the previous model coordinate to ``is_main`` = False
        **Note**
        Check also that the new is right main
        """
        pc1 = self.model_coordinate.create({
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
            'is_main': True,
        })
        pc2 = self.model_coordinate.create({
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_2,
            'is_main': True,
        })
        self.assertFalse(
            pc1.is_main, 'Previous model Coordinate Should Not Be Main')
        self.assertTrue(pc2.is_main, 'New model Coordinate Should Be Main')
        return

    def test_check_at_least_one_main(self):
        """
        Test the fact that the associated partner of the model coordinate has
        at least one main coordinate.
        """
        # Clean existing coordinates
        self.model_coordinate.search([
            ('partner_id', '=', self.partner1.id),
        ]).unlink()
        pc = self.model_coordinate.create({
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
            'is_main': False,
        })
        self.assertEqual(pc.is_main, True,
                         'First model Coordinate Must Be Main')
        return

    def test_set_as_main(self):
        """
        Test the behavior of ``_set_as_main``
        Context:
        model_coo_1 : main     active
        model_coo_2 : not main active

        Waiting result:
        model_coo_1 : main    not active
        model_coo_2 : main    active
        """
        # Clean existing coordinates
        self.model_coordinate.search([
            ('partner_id', '=', self.partner1.id),
        ]).unlink()
        pc1 = self.model_coordinate.create({
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
            'is_main': True,
        })
        pc2 = self.model_coordinate.create({
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_2,
            'is_main': False,
        })
        pc2.with_context(invalidate=True)._set_as_main()
        coordinate = self.partner1[self.coo_into_partner]
        self.assertTrue(pc1.is_main)
        self.assertFalse(pc1.active)
        self.assertTrue(pc2.is_main)
        self.assertTrue(pc2.active)
        self.assertTrue(
            coordinate.id == pc2.id,
            'Replication Failed: Should be the new selected as main model '
            'coordinate')
        return

    def test_bad_unlink_abstract_coordinate(self):
        """
        * creation of two model coordinate that have the same
              type and the same partner
        * try to unlink the main coordinate
        * check that is raise an ``orm.except_orm`` exception
        """
        main_abstract_coordinate = self.model_coordinate.create({
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
            'is_main': True,
        })
        self.model_coordinate.create({
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_2,
            'is_main': False,
        })
        with self.assertRaises(ValidationError):
            main_abstract_coordinate.unlink()
        return

    def test_correct_unlink_abstract_coordinate(self):
        """
        * creation of two model coordinate that have the same
              type and the same partner
        * try to unlink the two main coordinate
        * check that it succeed
        """
        self.model_coordinate.create({
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
            'is_main': True,
        })
        self.model_coordinate.create({
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_2,
            'is_main': False,
        })
        # We have to load every coordinates (even if created by others
        # models)
        coordinates = self.model_coordinate.search([
            ('partner_id', '=', self.partner1.id),
        ])
        self.assertTrue(coordinates.unlink(),
                        'Should be able to delete all coordinate of the same '
                        'type for the same partner')
        return

    def check_state_of_duplicate(self, is_duplicate_values, detected=None):
        for is_duplicate_value in is_duplicate_values:
            if detected is None:
                self.assertFalse(
                    is_duplicate_value['is_duplicate_detected'],
                    'Should be duplicate detected')
                self.assertFalse(
                    is_duplicate_value['is_duplicate_allowed'],
                    'Should not be duplicate allowed')
            else:
                if detected:
                    self.assertTrue(
                        is_duplicate_value['is_duplicate_detected'],
                        'Should be duplicate detected')
                    self.assertFalse(
                        is_duplicate_value['is_duplicate_allowed'],
                        'Should not be duplicate allowed')
                else:
                    self.assertTrue(
                        is_duplicate_value['is_duplicate_allowed'],
                        'Should be duplicate allowed')
                    self.assertFalse(
                        is_duplicate_value['is_duplicate_detected'],
                        'Should not be duplicate detected')

    def get_value_detected(self, coordinates):
        return coordinates.read([
            'is_duplicate_detected',
            'is_duplicate_allowed',
        ])

    def test_management_of_duplicate_create(self):
        """
        * create two model coordinate with same model_id
          check that ``is_duplicate_detected`` is set to True
          check that ``is_duplicate_allowed`` is set to False
        * allow those two model coordinate
          check that ``is_duplicate_detected`` is set to False
          check that ``is_duplicate_allowed`` is set to True
        * create a third model coordinate with same model_id than
          previous
          check that ``is_duplicate_detected`` is set to True
          check that ``is_duplicate_allowed`` is set to False
        """
        coordinate1 = self.model_coordinate.create({
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
        })
        coordinate2 = self.model_coordinate.create({
            'partner_id': self.partner2.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
        })
        coordinates = coordinate1 | coordinate2
        is_duplicate_values = self.get_value_detected(coordinates)
        self.check_state_of_duplicate(is_duplicate_values, True)
        coordinates = coordinate1 | coordinate2
        coordinates.write({
            'is_duplicate_detected': False,
            'is_duplicate_allowed': True,
        })
        is_duplicate_values = self.get_value_detected(coordinates)
        self.check_state_of_duplicate(is_duplicate_values, False)

        self.model_coordinate.create({
            'partner_id': self.partner3.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
        })
        is_duplicate_values = self.get_value_detected(coordinates)
        self.check_state_of_duplicate(is_duplicate_values, True)

    def test_management_of_duplicate_unlink(self):
        """
        * create two model coordinate with same model_id
        * allow those tow model coordinate
        * unlink on of those coordinate
          check that ``is_duplicate_detected`` is set to False
          check that ``is_duplicate_allowed`` is set to False
        """
        coordinate1 = self.model_coordinate.create({
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
        })
        coordinate2 = self.model_coordinate.create({
            'partner_id': self.partner2.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
        })
        coordinate2.unlink()
        is_duplicate_values = self.get_value_detected(coordinate1)
        self.check_state_of_duplicate(is_duplicate_values)
        return

    def test_management_of_duplicate_invalidate(self):
        """
        * create two model coordinate with same model_id
        * allow those tow model coordinate
        * invalidate first coordinate
          check that the active one ``is_duplicate_detected`
               is set to False
          check that the active one ``is_duplicate_allowed``
              is set to False
        """
        coordinate1 = self.model_coordinate.create({
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
        })
        coordinate2 = self.model_coordinate.create({
            'partner_id': self.partner2.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
        })
        coordinate2.action_invalidate()
        is_duplicate_values = self.get_value_detected(coordinate1)
        self.check_state_of_duplicate(is_duplicate_values)
        return

    def test_bad_invalidate(self):
        """
        * create three models coordinate with same model_id for the
            same partner
        * invalidate main coordinate
        * check that it fails
        """
        # Clean existing coordinates
        self.model_coordinate.search([
            ('partner_id', '=', self.partner1.id),
        ]).unlink()
        vals = {
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
        }
        coordinate = self.model_coordinate.create(vals)
        vals = {
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_2,
        }
        self.model_coordinate.create(vals)
        vals = {
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_3,
        }
        self.model_coordinate.create(vals)
        with self.assertRaises(ValidationError):
            coordinate.action_invalidate()
        return

    def test_autoswitch_main_on_invalidate(self):
        """
        * create 2 models coordinate with same model_id for the
            same partner
        * invalidate main coordinate
        * check if the second one is now the main coordinate
        """
        # Clean existing coordinates
        self.model_coordinate.search([
            ('partner_id', '=', self.partner1.id),
        ]).unlink()
        vals = {
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
        }
        coordinate1 = self.model_coordinate.create(vals)
        vals = {
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_2,
        }
        coordinate2 = self.model_coordinate.create(vals)
        coordinate1.action_invalidate()
        self.assertTrue(coordinate2.is_main)
        return
