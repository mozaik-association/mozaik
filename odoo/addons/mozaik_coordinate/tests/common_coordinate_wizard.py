# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4
from odoo.fields import first
from .common import CommonCoordinate


class CommonCoordinateWizard(CommonCoordinate):
    """
    Tests for change.main.coordinate wizard.
    Contains some tests to execute with others wizard who implements this one.
    """

    def setUp(self):
        super(CommonCoordinateWizard, self).setUp()
        self.partner_obj = self.env['res.partner']
        self.partner1 = self.env.ref("mozaik_coordinate.res_partner_thierry")
        self.partner2 = self.env.ref("mozaik_coordinate.res_partner_pauline")
        self.partner3 = self.env.ref("mozaik_coordinate.res_partner_nicolas")
        self.partner4 = self.env.ref("mozaik_coordinate.res_partner_sandra")
        self.model_id_1 = str(uuid4())
        self.field_id_1 = str(uuid4())
        self.field_id_2 = str(uuid4())

    def change_main_coordinate(self, invalidate):
        """
        Create and trigger the wizard to change the main coordinate
        :param invalidate: bool
        :return: dict
        """
        coordinates = self.coordinate1 | self.coordinate2
        context = self.env.context.copy()
        context.update({
            'active_model': self.model_coordinate._name,
            'active_ids': coordinates.ids,
            'target_model': self.model_coordinate._name,
        })
        disc_value = first(coordinates)._get_discriminant_value()
        wiz_vals = {
            self.model_coordinate._discriminant_field: disc_value,
            'invalidate_previous_coordinate': invalidate,
        }
        wizard = self.model_coordinate_wizard.with_context(
            context).create(wiz_vals)
        return wizard.button_change_main_coordinate()

    def switch_main_coordinate(self, new_main_coordinate, invalidate):
        """

        :param new_main_coordinate: abstract.coordinate recordset
        :param invalidate: bool
        :return: dict
        """
        context = self.env.context.copy()
        context.update({
            'active_model': new_main_coordinate._name,
            'active_id': new_main_coordinate.partner_id.id,
            'res_id': new_main_coordinate.partner_id.id,
            'target_id': new_main_coordinate.id,
            'active_ids': new_main_coordinate.partner_id.ids,
            'target_model': 'res.partner',
        })
        value = new_main_coordinate._get_discriminant_value()
        wiz_vals = {
            self.model_coordinate._discriminant_field: value,
            'invalidate_previous_coordinate': invalidate,
        }
        wizard = self.model_coordinate_wizard.with_context(
            context).create(wiz_vals)
        context.update({
            'active_id': new_main_coordinate.id,
            'active_ids': new_main_coordinate.ids,
            'active_model': self.model_coordinate._name,
            'target_model': self.model_coordinate._name,
            'mode': 'switch',
        })
        return wizard.with_context(context).button_change_main_coordinate()

    def test_mass_replication(self):
        """
        Test that created coordinates are main for their respective partners.

        Assure that the main coordinate is well replicated into the partner
            form partner[coo_into_partner] = self.model_id_N
        Assure that the replicated coordinate is main:
            partner[coo_into_partner].is_main = True
        """
        self.change_main_coordinate(True)
        partners = self.partner1 | self.partner2 | self.partner3
        values = {
            'partner_id': self.partner1.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
            'is_main': True,
        }
        self.model_coordinate.create(values)
        values = {
            'partner_id': self.partner2.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
            'is_main': True,
        }
        self.model_coordinate.create(values)
        values = {
            'partner_id': self.partner3.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
            'is_main': True,
        }
        self.model_coordinate.create(values)
        for partner in partners:
            coordinate = partner[self.coo_into_partner]
            coord_value = coordinate._get_discriminant_value()
            value = coord_value == self.field_id_1 and coordinate.is_main
            self.assertTrue(
                value, 'Coordinate Should Be Replicate Into The Associated '
                       'Partner')
        return

    def test_mass_replication_with_invalidate(self):
        """
        This test check the fact that the ``mass_select_as_main`` of
        the wizard will right invalidate the previous model coordinate if it is
        wanted
        Check also the fact that if a selected partner has already the new
        selected number
        into a model coordinate then it will not be invalidate
        **Note**
        Context:
        u1 ----- main_model_coo1 ------ model 1 : active
        u2 ----- main_model_coo2 ------ model 2 : active
        u2 ----- model_coo_3 ---------- model 1 : active
        Excepted Result:

        u1 ----- main_model_coo1 ------ model 1 : active
        u2 ----- model_coo2      ------ model 2 : not active
        u2 ----- main_model_coo_3------ model 1 : active
        """
        self.assertTrue(self.coordinate1.active)
        self.assertTrue(self.coordinate2.active)
        self.change_main_coordinate(True)
        self.assertTrue(
            self.coordinate1.active,
            'Should not invalidate a model coordinate that is already the '
            'main for the selected partner with this selected number')
        self.assertFalse(
            self.coordinate2.active,
            'Previous model Coordinate should be invalidate')
        return

    def test_mass_replication_without_invalidate(self):
        """
        This test check the fact that the ``mass_select_as_main`` of
        the wizard doesn't invalidate the previous model coordinate if it is
        not wanted
        **Note**
        Context:

        u1 ----- main_model_coo1 ------ model 1 : active
        u2 ----- main_model_coo2 ------ model 2 : active
        u2 ----- model_coo_3 ---------- model 1 : active
        Excepted Result:

        u1 ----- main_model_coo1 ------ model 1 : active
        u2 ----- model_coo2      ------ model 2 : active
        u2 ----- main_model_coo_3------ model 1 : active
        """
        self.change_main_coordinate(False)
        self.assertTrue(
            self.coordinate2.active,
            'Previous model Coordinate should not be invalidate')
        return

    def test_switch_main_coordinate(self):
        """
        This test check the ability of the wizard
        to set a selected coordinate as main, unflag the current one
        and eventually invalidate it
        """
        vals = {
            'partner_id': self.partner4.id,
            self.model_coordinate._discriminant_field: self.field_id_1,
        }
        coordinate1 = self.model_coordinate.create(vals)
        vals = {
            'partner_id': self.partner4.id,
            self.model_coordinate._discriminant_field: self.field_id_2,
        }
        coordinate2 = self.model_coordinate.create(vals)
        self.switch_main_coordinate(coordinate2, False)
        self.assertFalse(coordinate1.is_main)
        self.assertTrue(coordinate1.active)
        self.assertTrue(coordinate2.is_main)

        self.switch_main_coordinate(coordinate1, True)
        self.assertTrue(coordinate1.is_main)
        self.assertFalse(coordinate2.active)
        return
