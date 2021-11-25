# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestMembershipRequest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.mr_model = self.env["membership.request"]
        self.belgium = self.env["res.country"].search([("code", "=", "BE")])
        self.city_lg = self.env["res.city"].create(
            {
                "name": "Liège",
                "int_instance_id": self.browse_ref(
                    "mozaik_structure.int_instance_01"
                ).id,
                "zipcode": "4000",
                "country_id": self.belgium.id,
            }
        )
        self.federal = self.browse_ref("mozaik_structure.int_instance_01")

    def _add_technical_name(self, mr):
        """Onchanges are not triggered in tests, so
        we need to compute technical_name explicitly."""
        tech_name = self.env["membership.request"].get_technical_name(
            mr.address_local_street_id,
            mr.city_id.id,
            mr.number,
            mr.box,
            mr.city_man,
            mr.street_man,
            mr.zip_man,
            mr.country_id.id,
        )
        mr.write({"technical_name": tech_name})

    def test_no_val_explicit_skip(self):
        """
        Creating a mr and explicitly deactivating
        auto_validation.
        """
        # auto_accept_membership: Nok - explicit skip
        mr = self.mr_model.create(
            {
                "lastname": "DUJARDIN",
                "firstname": "Jean",
                "gender": "male",
                "street_man": False,
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "request_type": "m",
                "email": "jean@duj.fr",
            }
        )
        self._add_technical_name(mr)
        mr._auto_validate(False)
        self.assertFalse(mr.partner_id)
        self.assertEqual("draft", mr.state)

    def test_no_auto_val_no_email(self):
        """
        A membership request created without email,
        shouldn't be auto validated.
        """
        # auto-validate: Nok - no email
        mr = self.mr_model.create(
            {
                "lastname": "DUJARDIN",
                "firstname": "Pierre",
                "gender": "male",
                "street_man": False,
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "request_type": "m",
            }
        )
        self._add_technical_name(mr)
        mr._auto_validate(True)
        self.assertFalse(mr.partner_id)
        self.assertEqual("draft", mr.state)

    def test_auto_val_with_city_only(self):
        """
        Classic case: only the city and the zip code are given
        amongst address parameters. Membership request
        should be auto-validated.
        """
        mr = self.mr_model.create(
            {
                "lastname": "DUJARDIN",
                "firstname": "Pierre-Yves",
                "gender": "male",
                "country_id": self.belgium.id,
                "street_man": False,
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "request_type": "m",
                "email": "filou@duj.fr",
            }
        )
        self._add_technical_name(mr)
        mr._auto_validate(True)
        self.assertTrue(mr.partner_id)
        self.assertEqual(mr.partner_id.address_address_id.zip, self.city_lg.zipcode)
        self.assertEqual("validate", mr.state)

    def test_no_auto_val_26993_2_1_1(self):
        """
        A membership request created without verifying
        #26993/2.1.1 shouldn't be auto validated.
        """
        mr = self.mr_model.create(
            {
                "lastname": "DUJARDIN",
                "firstname": "Philippe",
                "gender": "male",
                "country_id": self.belgium.id,
                "street_man": "Rue Vaut-Rien",
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "request_type": "m",
                "email": "filou@duj.fr",
                "mobile": "+33.6.24.61.19.81",
            }
        )
        self._add_technical_name(mr)
        mr._auto_validate(True)
        self.assertFalse(mr.partner_id)
        self.assertEqual("draft", mr.state)

    def test_unrecognized_address(self):
        """
        When entering zip manually (to avoid for addresses in Belgium)
        the address is created using this zip.
        """
        # auto-validate: Ok - 26993/2.1.2 - unrecognized or foreign zipcode
        mr = self.mr_model.create(
            {
                "lastname": "DUJARDIN",
                "firstname": "Patrick",
                "gender": "male",
                "country_id": self.belgium.id,
                "street_man": False,
                "zip_man": "Cedex 99800",
                "city_id": False,
                "request_type": "m",
                "email": "patrick@duj.fr",
            }
        )
        self._add_technical_name(mr)
        mr._auto_validate(True)
        self.assertEqual("validate", mr.state)
        self.assertEqual(mr.partner_id.int_instance_id, self.federal)
        self.assertEqual(mr.partner_id.address_address_id.zip_man, "Cedex 99800")
        self.assertEqual(mr.partner_id.address_address_id.zip, "Cedex 99800")

    def test_auto_val_26993_2_1_3(self):
        mr = self.mr_model.create(
            {
                "lastname": "DUJARDIN",
                "firstname": "Kevin",
                "gender": "male",
                "country_id": self.belgium.id,
                "street_man": False,
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "request_type": "m",
                "email": "kevin@duj.fr",
            }
        )
        self._add_technical_name(mr)
        mr._auto_validate(True)
        self.assertEqual("validate", mr.state)
        self.assertEqual(self.city_lg.int_instance_id, mr.partner_id.int_instance_id)
        self.assertEqual(self.city_lg.zipcode, mr.address_id.zip)

    # def test_no_autoval_26993_2_3_2(self):
    #     """
    #     When creating a membership request, if the partner
    #     is recognized but the firstname and lastname are
    #     not the same on the membership request and on
    #     the partner form, then no autovalidation.
    #     """
    #     thierry = self.env["res.partner"].create(
    #         {
    #             "firstname": "Thierry",
    #             "lastname": "Dujardin",
    #             "email": "thierry@gmail.com",
    #         }
    #     )
    #     mr = self.mr_model.create(
    #         {
    #             "lastname": "Dujardin",
    #             "firstname": "Denis",
    #             "gender": "male",
    #             "request_type": "m",
    #             "email": "thierry@gmail.com",
    #         }
    #     )
    #     # we have to call onchange method explicitly to find the associated partner
    #     mr.onchange_partner_component()
    #     self._add_technical_name(mr)
    #     mr._auto_validate(True)
    #     self.assertTrue(mr.partner_id)
    #     self.assertEqual(thierry, mr.partner_id)
    #     self.assertEqual("draft", mr.state)

    def test_no_autoval_email_not_unique(self):
        """
        When the email adress is not unique, no autovalidation
        #26993/2.2
        """
        self.env["res.partner"].create(
            {"lastname": "dupont", "firstname": "pauline", "email": "pauline@gmail.com"}
        )
        self.env["res.partner"].create(
            {
                "lastname": "dumoulin",
                "firstname": "pauline",
                "email": "pauline@gmail.com",
            }
        )
        mr = self.mr_model.create(
            {
                "lastname": "LHERMITTE",
                "firstname": "Thierry",
                "gender": "male",
                "request_type": "m",
                "email": "pauline@gmail.com",
            }
        )
        self._add_technical_name(mr)
        mr._auto_validate(True)
        self.assertEqual("draft", mr.state)

    # def test_no_autoeval_with_conflictual_status(self):
    #     marc = self.env["res.partner"].create(
    #         {
    #             "lastname": "Lavoine",
    #             "firstname": "Marc",
    #             "email": "marc.lavoine@test.com",
    #             "accepted_date": fields.Date.today(),
    #             "free_member": True,
    #         }
    #     )
    #     # make marc a supporter
    #     supporter = self.env["membership.state"].search([("code", "=", "supporter")])
    #     marc.write({"membership_state_id": supporter.id})
    #     self.assertEqual(marc.membership_state_code, "supporter")
    #     marc.action_resignation()
    #     self.assertEqual("former_supporter", marc.membership_state_code)
    #
    #     mr = self.mr_model.create(
    #         {
    #             "lastname": "Lavoine",
    #             "firstname": "Marc",
    #             "gender": "male",
    #             "request_type": "m",
    #             "email": "marc.lavoine@test.com",
    #         }
    #     )
    #     # we have to call onchange method explicitly to find the associated partner
    #     mr.onchange_partner_component()
    #     self._add_technical_name(mr)
    #     mr._auto_validate(True)
    #     self.assertTrue(mr.partner_id)
    #     self.assertEqual("draft", mr.state)
