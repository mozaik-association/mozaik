# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader

from odoo.tests.common import SavepointCase


class TestPrivacyDomainMixin(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models import (  # pylint: disable=import-outside-toplevel
            ResCountryWithPrivacyDomain,
        )

        cls.loader.update_registry((ResCountryWithPrivacyDomain,))

        cls.public_country = cls.env.ref("base.be")
        cls.private_country = cls.env.ref("base.fr")
        cls.private_country.domain = "[('email', '!=', False)]"

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_domain_is_set(self):
        self.assertTrue(self.private_country.domain_is_set)
        self.assertFalse(self.public_country.domain_is_set)
        private_countries = self.env["res.country"].search(
            [("domain_is_set", "=", True)]
        )
        self.assertEqual(private_countries, self.private_country)

    def test_filter_allowed_for_partner(self):
        partner = self.env["res.partner"].create({"name": "Harry Potter"})
        allowed_countries = (
            self.public_country | self.private_country
        )._filter_allowed_for_partner(partner.id)
        self.assertEqual(allowed_countries, self.public_country)
        partner.email = "harry.potter@hogwarts.com"
        allowed_countries = (
            self.public_country | self.private_country
        )._filter_allowed_for_partner(partner.id)
        self.assertEqual(len(allowed_countries), 2)
