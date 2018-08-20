# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestEmailCoordinate(TransactionCase):

    def setUp(self):
        super(TestEmailCoordinate, self).setUp()
        self.mobile4 = self.env.ref("mozaik_phone.phone_phone_mobile3")
        self.mobile5 = self.env.ref("mozaik_phone.phone_phone_mobile4")
        self.fix1 = self.env.ref("mozaik_phone.phone_phone_fix1")
        self.fix2 = self.env.ref("mozaik_phone.phone_phone_fix2")
        self.phone_coord9 = self.env.ref("mozaik_phone.phone_coordinate4")
        self.phone_coord10 = self.env.ref("mozaik_phone.phone_coordinate5")
        self.phone_coord11 = self.env.ref("mozaik_phone.phone_coordinate6")
        self.phone_coord12 = self.env.ref("mozaik_phone.phone_coordinate7")
        self.wizard_obj = self.env['change.phone.type']

    def test_change_main_mobile_to_fix_main(self):
        """
        Trying to change mobile4 (main) from mobile to fix and
        set is as main in the new category.
        Expected results are:
        - mobile4 type should be FIX
        - mobile_coordinate_for_jacques_1 type should be FIX and MAIN
        - mobile_coordinate_for_jacques_2 should become main
        - fix_coordinate_for_jacques_1 should not be main anymore
        """
        wizard = self.wizard_obj.new({
            'phone_id': self.phone_coord9.phone_id.id,
            'type': 'fix',
        })
        wizard.change_phone_type()
        self.assertEqual(self.phone_coord9.phone_id.type, 'fix')
        self.assertEqual(self.phone_coord9.coordinate_type, 'fix')
        self.assertTrue(self.phone_coord10.is_main)
        # There already have 1 main (the coord11) so the new is not the main
        self.assertFalse(self.phone_coord9.is_main)
        self.assertTrue(self.phone_coord11.is_main)
        return

    def test_change_main_mobile_to_fix_no_main(self):
        """
        Trying to change mobile4 (main) from mobile to fix but
        do not set it as main in the new category.
        Expected results are:
        - mobile4 type should be FIX
        - mobile_coordinate_for_jacques_1 type should be FIX and not MAIN
        - mobile_coordinate_for_jacques_2 should become main
        - fix_coordinate_for_jacques_1 should be main anymore
        """
        wizard = self.wizard_obj.new({
            'phone_id': self.mobile4.id,
            'type': 'fix',
            'is_main': False,
        })
        wizard.change_phone_type()
        self.assertEqual(self.mobile4.type, 'fix')
        self.assertEqual(self.phone_coord9.coordinate_type, 'fix')
        self.assertTrue(self.phone_coord10.is_main)
        self.assertFalse(self.phone_coord9.is_main)
        self.assertTrue(self.phone_coord11.is_main)
        return

    def test_change_not_main_mobile_to_fix_main(self):
        """
        Trying to change mobile5 (not main) from mobile to fix and
        set is as main in the new category.
        Expected results are:
        - mobile5 type should be FIX
        - mobile_coordinate_for_jacques_2 type should be FIX and MAIN
        - mobile_coordinate_for_jacques_1 should remain main
        - fix_coordinate_for_jacques_1 should not be main anymore
        """
        wizard = self.wizard_obj.new({
            'phone_id': self.phone_coord10.phone_id.id,
            'type': 'fix',
        })
        wizard.change_phone_type()
        self.assertEqual(self.phone_coord10.phone_id.type, 'fix')
        self.assertEqual(self.phone_coord10.coordinate_type, 'fix')
        self.assertTrue(self.phone_coord9.is_main)
        self.assertFalse(self.phone_coord10.is_main)
        self.assertTrue(self.phone_coord11.is_main)
        return

    def test_change_not_main_mobile_to_fix_no_main(self):
        """
        Trying to change mobile5 (not main) from mobile to fix and
        do not set is as main in the new category.
        Expected results are:
        - mobile5 type should be FIX
        - mobile_coordinate_for_jacques_2 type should be FIX and should
          remain not main
        - mobile_coordinate_for_jacques_1 should remain main
        - fix_coordinate_for_jacques_1 should remain main
        """
        wizard = self.wizard_obj.new({
            'phone_id': self.mobile5.id,
            'type': 'fix',
            'is_main': False,
        })
        wizard.change_phone_type()
        self.assertEqual(self.mobile5.type, 'fix')
        self.assertEqual(self.phone_coord10.coordinate_type, 'fix')
        self.assertTrue(self.phone_coord9.is_main)
        self.assertFalse(self.phone_coord10.is_main)
        self.assertTrue(self.phone_coord11.is_main)
        return
