# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestResCity(TransactionCase):
    def test_default_country_id(self):
        """
        Check for default country
        """
        # reset countries
        self.env["res.country"].search([("enforce_cities", "=", True)]).write(
            {
                "enforce_cities": False,
            }
        )
        # Belgium does not enforce cities
        def_country = self.env["res.city"]._default_country_id()
        self.assertFalse(def_country)
        # enforce cities
        self.env["res.country"]._country_default_get("BE")["enforce_cities"] = True
        def_country = self.env["res.city"]._default_country_id()
        self.assertTrue(def_country)
        return

    def test_res_city(self):
        c1 = self.env.ref("mozaik_address.res_city_1")
        self.assertEqual(c1.display_name, c1.zipcode + " " + c1.name)
        c1.zipcode = "2541"
        c1.invalidate_cache()
        self.assertEqual(c1.display_name, c1.zipcode + " " + c1.name)
