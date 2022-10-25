# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import TransactionCase


class MembershipRequestTest(TransactionCase):
    def setUp(self):
        """
        We need to explicitly update the DB otherwise
        virtual.custom.partner info is not always correctly
        updated.
        """
        super().setUp()
        partner_obj = self.env["res.partner"]
        self.jean = partner_obj.create(
            {
                "lastname": "Dujardin",
                "firstname": "Jean",
            }
        )
        self.jean.flush()
        self.omar = partner_obj.create(
            {
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "o.s@test.com",
                "phone": "043681234",
                "birthdate_date": date(1978, 1, 20),
            }
        )
        self.omar.flush()
        # Homonym (so same firsntame and lastname) but different
        # other data.
        self.omar2 = partner_obj.create(
            {
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "os@test.com",
                "phone": "043689876",
                "birthdate_date": date(1980, 4, 15),
            }
        )
        self.omar2.flush()
        # Omar's wife using the same email address
        self.omar_wife = partner_obj.create(
            {"lastname": "Sy", "firstname": "Wife", "email": "o.s@test.com"}
        )
        self.omar_wife.flush()

    def test_sensitive_data(self):
        """
        Define the following sensitive data:
        "[lastname, firstname, email, birthdate_date, phone, mobile]"

        FIRST MEMBERSHIP REQUEST
        Change his firstname -> sensitive
        Add a phone -> not sensitive since was empty
        Add a birthdate -> not sensitive since was empty

        SECOND MEMBERSHIP REQUEST
        Change phone to format it -> not sensitive
        Add mobile and email -> not sensitive

        THIRD MEMBERSHIP REQUEST
        Changing phone number -> sensitive
        """
        # We set specific sensitive data.
        self.env["ir.config_parameter"].sudo().set_param(
            "membership.request.sensitive.fields",
            "[lastname, firstname, email, birthdate_date, phone, mobile]",
        )

        # 1st membership request
        mr_obj = self.env["membership.request"]
        phone = "0479123456"
        birthdate = date(1972, 6, 19)
        mr = mr_obj.create(
            {
                "partner_id": self.jean.id,
                "lastname": self.jean.lastname,
                "firstname": "Jean Edmond",
                "phone": phone,
                "birthdate_date": birthdate,
            }
        )
        mr.validate_request()
        self.assertEqual(self.jean.firstname, "Jean", "Firstname shouldn't be modified")
        self.assertEqual(self.jean.phone, phone, "Phone was set")
        self.assertEqual(self.jean.birthdate_date, birthdate, "Birthdate was set")

        # 2nd membership request
        phone = mr_obj.get_format_phone_number("0479123456")
        mobile = "123456"
        email = "test@test.com"
        mr = mr_obj.create(
            {
                "partner_id": self.jean.id,
                "lastname": self.jean.lastname,
                "phone": phone,
                "mobile": mobile,
                "email": email,
            }
        )
        mr.validate_request()
        self.assertEqual(
            self.jean.phone, phone, "Phone should be modified since just formatting"
        )
        self.assertEqual(
            self.jean.mobile, mobile, "Adding new mobile should be permitted"
        )
        self.assertEqual(
            self.jean.email, email, "Adding new mobile should be permitted"
        )

        # 3rd membership request
        phone = "0123456789"
        mr = mr_obj.create(
            {
                "partner_id": self.jean.id,
                "lastname": self.jean.lastname,
                "phone": phone,
            }
        )
        mr.validate_request()
        self.assertEqual(
            self.jean.phone,
            mr_obj.get_format_phone_number("0479123456"),
            "Phone shouldn't be changed",
        )
