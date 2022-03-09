# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import TransactionCase


class TestComputeFirstname(TransactionCase):
    def setUp(self):
        """
        Initialisation:
            The order for partner names is set at '[firstname] [lastname]'
            self.petition is a petition
            self.partner is a partner
        """
        super().setUp()
        self.partner_names_order = (self.env["res.config.settings"]).create(
            {"partner_names_order": "first_last"}
        )
        self.milestone = self.env["petition.milestone"].create({"value": 1})
        self.petition = (self.env["petition.petition"]).create(
            {
                "title": "test_petition",
                "date_begin": date(2021, 10, 25),
                "date_end": date(2021, 10, 27),
                "milestone_ids": [(6, 0, self.milestone.id)],
            }
        )
        self.partner = (self.env["res.partner"]).create({"name": "Jean Dupont"})

    def test_name_from_firstname_lastname(self):
        """
        Data:
            self.signatory: a signatory to a petition with given firstname and lastname
        Test case:
            The signatory's full name is computed correctly
        """
        firstname = "Jean"
        lastname = "Dupont"
        self.signatory = (self.env["petition.registration"]).create(
            {
                "petition_id": self.petition.id,
                "firstname": firstname,
                "lastname": lastname,
                "email": "test@test.com",
            }
        )
        self.assertEqual(self.signatory.name, "Jean Dupont")

    def test_firstname_lastname_from_name(self):
        """
        Data:
            self.signatory: a signatory to a petition with a given name
        Test case:
            The signatory's firstname and lastname are computed correctly
        """
        self.signatory = (self.env["petition.registration"]).create(
            {
                "petition_id": self.petition.id,
                "name": "Jean Dupont",
                "email": "test@test.com",
            }
        )
        self.assertEqual(self.signatory.firstname, "Jean")
        self.assertEqual(self.signatory.lastname, "Dupont")

    def test_change_registration_doesnt_change_partner(self):
        """
        Data:
            self.partner: a partner whose name is "Jean Dupont"
            self.signatory: a signatory whose partner.id is self.partner
        Test case:
            Changing the first name or last name of the signatory does not affect
            the res.partner name
        """
        self.signatory = (self.env["petition.registration"]).create(
            {
                "petition_id": self.petition.id,
                "partner_id": self.partner.id,
                "email": "test@test.com",
            }
        )
        self.assertEqual(self.signatory.firstname, "Jean")
        self.assertEqual(self.signatory.lastname, "Dupont")

        # Changing firstname
        self.signatory.firstname = "Jeanne"
        self.assertEqual(self.signatory.firstname, "Jeanne")
        self.assertEqual(self.partner.firstname, "Jean")

        # Changing lastname
        self.signatory.lastname = "Dubois"
        self.assertEqual(self.signatory.lastname, "Dubois")
        self.assertEqual(self.partner.lastname, "Dupont")

    def test_change_partner_change_registration(self):
        """
        Data:
            self.partner: a partner whose name is "Jean Dupont"
            self.signatory: a signatory whose partner.id is self.partner
        Test case:
            Changing the first name (resp., lastname) of the partner
            will change the first name (resp., lastname) automatically
            on the signatory form
        """
        self.signatory = (self.env["petition.registration"]).create(
            {
                "petition_id": self.petition.id,
                "partner_id": self.partner.id,
                "email": "test@test.com",
            }
        )
        self.assertEqual(self.signatory.firstname, "Jean")
        self.assertEqual(self.signatory.lastname, "Dupont")

        # Changing firstname of self.partner
        self.partner.firstname = "Jeanne"
        self.assertEqual(self.partner.firstname, "Jeanne")
        self.assertEqual(self.signatory.firstname, "Jeanne")

        # Changing lastname of self.partner
        self.partner.lastname = "Dubois"
        self.assertEqual(self.partner.lastname, "Dubois")
        self.assertEqual(self.signatory.lastname, "Dubois")
