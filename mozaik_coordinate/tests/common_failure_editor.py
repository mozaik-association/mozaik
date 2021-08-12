# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import IntegrityError
from .common import CommonCoordinate

DESC = "Bad Coordinate"


class CommonFailureEditor(CommonCoordinate):
    """
    Run test for the abstract class too
    resolved with a dual inherit on the abstract and the common.NAME
    """

    def setUp(self):
        super(CommonFailureEditor, self).setUp()
        self.model_wizard = self.env["failure.editor"]
        self.partner1 = self.env.ref("mozaik_coordinate.res_partner_thierry")
        self.model_coordinate = None
        self.coordinate = None

    def create_failure_data(self, inc):
        """
        Create a failure.editor wizard
        :param inc:
        :return: failure.editor wizard
        """
        context = self.env.context.copy()
        context.update(
            {
                "active_ids": self.coordinate.ids,
                "active_model": self.model_coordinate._name,
                "default_model": self.model_coordinate._name,
            }
        )
        wiz_vals = {
            "increase": inc,
            "description": DESC,
        }
        return self.model_wizard.with_context(context).create(wiz_vals)

    def test_add_failure(self):
        """
        1/ test reference data
        2/ create a valid wz
        3/ execute it and test the new counter value
        4/ reset the counter and test its value
        5/ create an invalid wz
        """
        # 1/ Check for reference data
        self.assertEqual(
            self.coordinate.failure_counter,
            0,
            "Wrong expected reference data for this test",
        )

        # 2/ Create wizard record
        counter = 2
        wizard = self.create_failure_data(counter)

        # 3/ Execute wizard
        wizard.update_failure_data()
        self.assertEqual(
            self.coordinate.failure_counter,
            counter,
            "Update coordinate fails with wrong failure_counter",
        )
        self.assertEqual(
            self.coordinate.failure_description,
            DESC,
            "Update coordinate fails with wrong failure_" "description",
        )

        # 4/ Reset counter
        self.coordinate.button_reset_counter()
        self.assertEqual(
            self.coordinate.failure_counter,
            0,
            "Reset counter fails with wrong failure_counter",
        )
        self.env.cr._default_log_exceptions = False
        with self.assertRaises(IntegrityError):
            self.create_failure_data(-2)
        self.env.cr._default_log_exceptions = True
        return
