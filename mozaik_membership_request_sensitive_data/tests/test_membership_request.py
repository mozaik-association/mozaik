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

    def test_sensitive_data_classic(self):
        """
        Define the following sensitive data:
        "[lastname, firstname, email, birthdate_date, phone, mobile]"

        1.
        Change his firstname -> sensitive
        Add a phone -> not sensitive since was empty
        Add a birthdate -> not sensitive since was empty

        2.
        Change phone to format it -> not sensitive
        Add mobile and email -> not sensitive

        3.
        Changing phone number -> sensitive

        4.
        Change firstname, lastname and email, but only capital letters
        -> not sensitive hence no message in the chatter.
        """
        # We set specific sensitive data.
        self.env["ir.config_parameter"].sudo().set_param(
            "membership.request.sensitive.fields",
            "[lastname, firstname, email, birthdate_date, phone, mobile]",
        )

        # 1.
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

        # 2.
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

        # 3.
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

        # 4.
        self.jean.email = "jd@test.com"
        mr = mr_obj.create(
            {
                "partner_id": self.jean.id,
                "lastname": "dujardin",
                "firstname": "jean",
                "email": "JD@test.com",
            }
        )
        mr.validate_request()
        # We should not have 'Sensitive data not modified' message in the chatter
        self.assertFalse(
            mr.message_ids.filtered(lambda message: "Sensitive data" in message.body)
        )

    def test_sensitive_data_address(self):
        """
        Set address as specific data.

        Create a partner without address.
        FIRST MEMBERSHIP REQUEST
        Add an address -> validated

        SECOND MEMBERSHIP REQUEST
        Change number of the address -> sensitive data wasn't modified.
        """
        # We set specific sensitive data.
        self.env["ir.config_parameter"].sudo().set_param(
            "membership.request.sensitive.fields",
            "[technical_name]",
        )
        mr_obj = self.env["membership.request"]
        partner_obj = self.env["res.partner"]

        harry = partner_obj.create({"lastname": "Potter", "firstname": "Harry"})

        # First membership request
        harry.button_modification_request()
        mr = mr_obj.search([("partner_id", "=", harry.id)])
        self.assertEqual(len(mr), 1)

        mr.write(
            {
                "country_id": self.env["res.country"].search([("code", "=", "BE")]).id,
                "city_id": self.env.ref("mozaik_address.res_city_1").id,
                "street_man": "Sous l'escalier",
                "number": "9",
            }
        )
        mr.validate_request()

        self.assertEqual(mr.state, "validate")

        harry_address = harry.address_address_id
        self.assertEqual(
            harry_address.city_id.id, self.env.ref("mozaik_address.res_city_1").id
        )
        self.assertEqual(harry_address.number, "9")

        # Second membership request
        harry.button_modification_request()
        mr = mr_obj.search([("partner_id", "=", harry.id)])
        self.assertEqual(len(mr), 1)

        mr.write({"number": "20"})
        self.assertEqual(mr.number, "20")
        mr.validate_request()
        self.assertEqual(harry.address_address_id.number, "9")
        self.assertFalse(mr.number)
