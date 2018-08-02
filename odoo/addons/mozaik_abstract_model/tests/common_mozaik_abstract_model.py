# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import exceptions, models


class CommonMozaikAbstractModel(object):
    """
    Tests for mozaik.abstract.model
    """

    def setUp(self):
        super().setUp()
        # Concrete Odoo models who inherit mozaik.abstract.model
        self.implemented_mozaik_abstract_obj = None
        # Odoo model with _inactive_cascade = True to disable records
        self.child_obj = None
        # Recordset for tests
        self.trigger1 = None
        self.child1 = None
        self.child2 = None
        # To avoid pylint error, use an empty list as default value
        self.invalidate_success = []
        self.invalidate_fails = []
        self.validates = []

    def _check_before_tests(self):
        """
        Do some check before start tests.
        To ensure data required are correctly initialized
        :return: bool
        """
        # Ensure correctly implemented
        self.assertTrue(self.trigger1._inactive_cascade)
        target_fields = self.implemented_mozaik_abstract_obj._fields.keys()
        self.assertIn('active', target_fields)
        self.assertIn('expire_date', target_fields)
        # Ensure tests can start
        self.assertTrue(self.trigger1)
        self.assertTrue(self.child1)
        self.assertTrue(self.child2)
        return True

    def test_disable_cascade1(self):
        """
        Test the abstract model to ensure that 'children' are correctly
        disabled (active = False)
        :return: bool
        """
        self._check_before_tests()
        # Ensure both are active = True
        self.assertTrue(self.trigger1.active)
        self.assertTrue(self.child1.active)
        self.assertTrue(self.child2.active)
        self.trigger1.write({
            'active': False,
        })
        # Ensure the trigger1 is disabled
        # And also the related Odoo record
        self.assertFalse(self.trigger1.active)
        self.assertFalse(self.child1.active)
        self.assertFalse(self.child2.active)
        return True

    def test_disable_cascade2(self):
        """
        Test that 'children' are not reactivate when the 'master' re-become
        active = True
        :return: bool
        """
        self._check_before_tests()
        # Ensure both are active = True
        self.assertTrue(self.trigger1.active)
        self.assertTrue(self.child1.active)
        self.assertTrue(self.child2.active)
        self.trigger1.write({
            'active': False,
        })
        # Ensure the trigger1 is disabled
        # And also the related Odoo record
        self.assertFalse(self.trigger1.active)
        self.assertFalse(self.child1.active)
        self.assertFalse(self.child2.active)
        self.trigger1.write({
            'active': True,
        })
        self.assertTrue(self.trigger1.active)
        self.assertFalse(self.child1.active)
        self.assertFalse(self.child2.active)
        return True

    def test_action_invalidate_success(self):
        """
        Test an invalidate who should work
        :return: bool
        """
        # Ensure test correctly implemented
        self.assertIsInstance(self.validates, models.BaseModel)
        result = self.invalidate_success.action_invalidate()
        self.assertTrue(result)
        for inv_success in self.invalidate_success:
            self.assertFalse(inv_success.active)
            self.assertTrue(bool(inv_success.expire_date))
        return True

    def test_action_invalidate_fail(self):
        """
        Test an invalidate who shouldn't work
        :return: bool
        """
        # Ensure test correctly implemented
        self.assertIsInstance(self.invalidate_fails, models.BaseModel)
        with self.assertRaises(exceptions.ValidationError):
            self.invalidate_fails.action_invalidate()
        return True

    def test_action_revalidate_success(self):
        """
        Test a revalidation who should work
        :return: bool
        """
        # Ensure test correctly implemented
        self.assertIsInstance(self.validates, models.BaseModel)
        result = self.validates.action_revalidate()
        self.assertTrue(result)
        for validate in self.validates:
            self.assertTrue(validate.active)
            self.assertFalse(bool(validate.expire_date))
        return True
