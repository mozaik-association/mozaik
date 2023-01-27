# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestUpdateMandateEndDateWizard:

    _module_ns = "mozaik_mandate"
    mandate = False
    model = False
    wizard = False

    def test_update_mandate_end_date(self):
        """
        Test 2 features of wizard:
            - set end date and inactivate an opened mandate
            - update end date of an inactive mandate
        """
        context = {
            "active_ids": [self.mandate.id],
            "active_model": self.model,
            "mode": "end_date",
        }
        tomorrow = date.today() + timedelta(days=1)
        last_week = date.today() - timedelta(days=7)
        last_month = date.today() - timedelta(days=30)

        wizard_object = self.env[self.wizard]
        wiz_id = wizard_object.with_context(context).create(
            {"mandate_end_date": tomorrow}
        )
        self.assertRaises(ValidationError, wiz_id.set_mandate_end_date)
        # Finish and inactive an opened mandate
        wiz_id.write({"mandate_end_date": last_week})
        wiz_id.set_mandate_end_date()
        self.assertFalse(self.mandate.active)
        self.assertEqual(self.mandate.end_date, last_week)

        # Update end date of a finished mandate
        wiz_id.write({"mandate_end_date": last_month})

        wiz_id.set_mandate_end_date()

        self.assertFalse(self.mandate.active)
        self.assertEqual(self.mandate.end_date, last_month)

    def test_reactivate_mandate(self):
        """
        Test the reactivation of an inactive mandate
        """
        context = {
            "active_ids": [self.mandate.id],
            "active_model": self.model,
            "mode": "reactivate",
        }
        last_week = date.today() - timedelta(days=7)
        last_month = date.today() - timedelta(days=30)
        next_month = date.today() + timedelta(days=30)

        wizard_object = self.env[self.wizard]

        # Inactivate mandate
        wiz_id = wizard_object.with_context(context).create(
            {"mandate_end_date": last_week}
        )
        wiz_id.set_mandate_end_date()
        self.assertFalse(self.mandate.active)

        # Reactivate mandate
        wiz_id = wizard_object.with_context(context).create(
            {"mandate_deadline_date": last_month}
        )
        self.assertRaises(ValidationError, wiz_id.reactivate_mandate)

        wiz_id.write({"mandate_deadline_date": next_month})

        wiz_id.reactivate_mandate()

        self.assertTrue(self.mandate.active)
        self.assertEqual(self.mandate.deadline_date, next_month)

    def test_reactivate_active_mandate(self):
        """
        Test the reactivation of an active mandate
        """
        context = {
            "active_ids": [self.mandate.id],
            "active_model": self.model,
            "mode": "reactivate",
        }
        next_month = date.today() + timedelta(days=30)

        wizard_object = self.env[self.wizard]

        self.assertTrue(self.mandate.active)

        # Reactivate mandate
        wiz_id = wizard_object.with_context(context).create(
            {"mandate_deadline_date": next_month}
        )
        self.assertEqual(
            wiz_id.message, "Some of the selected mandates are already active!"
        )


class TestUpdateStaMandateEndDateWizard(TestUpdateMandateEndDateWizard, SavepointCase):
    def setUp(self):
        self.mandate = self.browse_ref("%s.stam_paul_bourgmestre" % self._module_ns)
        self.model = "sta.mandate"
        self.wizard = "update.sta.mandate.end.date.wizard"
        super().setUp()

    def test_reactivate_mandate(self):
        return

    def test_reactivate_active_mandate(self):
        return


class TestUpdateIntMandateEndDateWizard(TestUpdateMandateEndDateWizard, SavepointCase):
    def setUp(self):
        self.mandate = self.browse_ref("%s.intm_paul_regional" % self._module_ns)
        self.model = "int.mandate"
        self.wizard = "update.int.mandate.end.date.wizard"
        super().setUp()


class TestUpdateExtMandateEndDateWizard(TestUpdateMandateEndDateWizard, SavepointCase):
    def setUp(self):
        self.mandate = self.browse_ref("%s.extm_paul_membre_ag" % self._module_ns)
        self.model = "ext.mandate"
        self.wizard = "update.ext.mandate.end.date.wizard"
        super().setUp()
