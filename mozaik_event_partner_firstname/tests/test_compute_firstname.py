from datetime import date

from odoo.tests.common import TransactionCase


class TestComputeFirstname(TransactionCase):
    def setUp(self):
        """
        Initialisation:
            The order for partner names is set at '[firstname] [lastname]'
            self.event is an event
            self.partner is a partner
        """
        super().setUp()
        self.partner_names_order = (self.env["res.config.settings"]).create(
            {"partner_names_order": "first_last"}
        )
        self.event = (self.env["event.event"]).create(
            {
                "name": "test_event",
                "date_begin": date(2021, 10, 25),
                "date_end": date(2021, 10, 27),
            }
        )
        self.partner = (self.env["res.partner"]).create({"name": "Jean Dupont"})

    def test_name_from_firstname_lastname(self):
        """
        Data:
            self.attendee: an attendee to an event with given firstname and lastname
        Test case:
            The attendee's full name is computed correctly
        """
        firstname = "Jean"
        lastname = "Dupont"
        self.attendee = (self.env["event.registration"]).create(
            {
                "event_id": self.event.id,
                "firstname": firstname,
                "lastname": lastname,
            }
        )
        self.assertEqual(self.attendee.name, "Jean Dupont")

    def test_firstname_lastname_from_name(self):
        """
        Data:
            self.attendee: an attendee to an event with a given name
        Test case:
            The attendee's firstname and lastname are computed correctly
        """
        self.attendee = (self.env["event.registration"]).create(
            {
                "event_id": self.event.id,
                "name": "Jean Dupont",
            }
        )
        self.assertEqual(self.attendee.firstname, "Jean")
        self.assertEqual(self.attendee.lastname, "Dupont")

    def test_change_registration_doesnt_change_partner(self):
        """
        Data:
            self.partner: a partner whose name is "Jean Dupont"
            self.attendee: an attendee whose partner.id is self.partner
        Test case:
            Changing the first name or last name of the attendee does not affect
            the res.partner name
        """
        self.attendee = (self.env["event.registration"]).create(
            {
                "event_id": self.event.id,
                "partner_id": self.partner.id,
            }
        )
        self.assertEqual(self.attendee.firstname, "Jean")
        self.assertEqual(self.attendee.lastname, "Dupont")

        # Changing firstname
        self.attendee.firstname = "Jeanne"
        self.assertEqual(self.attendee.firstname, "Jeanne")
        self.assertEqual(self.partner.firstname, "Jean")

        # Changing lastname
        self.attendee.lastname = "Dubois"
        self.assertEqual(self.attendee.lastname, "Dubois")
        self.assertEqual(self.partner.lastname, "Dupont")

    def test_change_partner_change_registration(self):
        """
        Data:
            self.partner: a partner whose name is "Jean Dupont"
            self.attendee: an attendee whose partner.id is self.partner
        Test case:
            Changing the first name (resp., lastname) of the partner
            will change the first name (resp., lastname) automatically
            on the attendee form
        """
        self.attendee = (self.env["event.registration"]).create(
            {
                "event_id": self.event.id,
                "partner_id": self.partner.id,
            }
        )
        self.assertEqual(self.attendee.firstname, "Jean")
        self.assertEqual(self.attendee.lastname, "Dupont")

        # Changing firstname of self.partner
        self.partner.firstname = "Jeanne"
        self.assertEqual(self.partner.firstname, "Jeanne")
        self.assertEqual(self.attendee.firstname, "Jeanne")

        # Changing lastname of self.partner
        self.partner.lastname = "Dubois"
        self.assertEqual(self.partner.lastname, "Dubois")
        self.assertEqual(self.attendee.lastname, "Dubois")
