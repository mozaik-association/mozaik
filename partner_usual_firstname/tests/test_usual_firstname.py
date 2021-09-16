# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestUsualFirstname(TransactionCase):
    def test_compute_and_sanitize(self):
        """
        Check for result of both compute and sanitize methods
        """
        poutine = self.env["res.partner"].create(
            {
                "name": "Poutine Vladimir",
            }
        )
        # native result from partner_firstname module
        self.assertEqual("Poutine Vladimir", poutine.name)
        self.assertEqual("Poutine", poutine.firstname)
        self.assertEqual("Vladimir", poutine.lastname)
        self.assertFalse(poutine.usual_firstname)
        self.assertFalse(poutine.usual_lastname)
        self.assertEqual(poutine.name, poutine.usual_name)
        # add an usual_firstname
        poutine.usual_lastname = "Vladinou"
        self.assertNotEqual(poutine.name, poutine.usual_name)
        self.assertEqual("Poutine Vladinou", poutine.usual_name)
        # add also an usual_lastname
        poutine.usual_firstname = "Poutinou"
        self.assertNotEqual(poutine.name, poutine.usual_name)
        self.assertEqual("Poutinou Vladinou", poutine.usual_name)
        # remove firstname
        poutine.write({"firstname": False})
        self.assertEqual("Poutinou", poutine.firstname)
        self.assertFalse(poutine.usual_firstname)
        self.assertEqual("Poutinou Vladinou", poutine.usual_name)
        # rollback to Poutine Vladimir
        poutine.name = "Poutine Vladimir"
        self.assertEqual("Poutine Vladinou", poutine.usual_name)
        # make a no sense update
        poutine.write(
            {
                "lastname": "Sarko",
                "firstname": False,
                "usual_lastname": "Sarko",
                "usual_firstname": "Nico",
            }
        )
        self.assertEqual("Nico Sarko", poutine.name)
        self.assertEqual("Nico", poutine.firstname)
        self.assertEqual("Sarko", poutine.lastname)
        self.assertFalse(poutine.usual_firstname)
        self.assertFalse(poutine.usual_lastname)
        self.assertEqual(poutine.name, poutine.usual_name)
        return

    def test_get_names(self):
        """
        Check for result of _get_names methods
        """
        ben = self.env["res.partner"].new(
            {
                "firstname": "Benoît",
                "lastname": "Poelvoorde",
                "usual_firstname": "Ben",
            }
        )
        self.assertEqual(["Poelvoorde", "Benoît"], ben._get_names())
        self.assertEqual(["Benoît", "Poelvoorde"], ben._get_names(reverse=True))
        self.assertEqual(["Poelvoorde", "Ben"], ben._get_names(usual=True))
        self.assertEqual(
            ["Ben", "Poelvoorde"], ben._get_names(reverse=True, usual=True)
        )
