# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import SavepointCase


class TestMembershipRequest(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mr_model = cls.env["membership.request"].with_context(mode="pre_process")
        cls.belgium = cls.env["res.country"].search([("code", "=", "BE")])
        cls.city_lg = cls.env["res.city"].create(
            {
                "name": "Liège",
                "zipcode": "4000",
                "country_id": cls.belgium.id,
            }
        )
        cls.city_namur = cls.env["res.city"].create(
            {
                "name": "Namur",
                "zipcode": "5000",
                "country_id": cls.belgium.id,
            }
        )
        cls.local_street = cls.env["address.local.street"].create(
            {
                "local_zip": "4000",
                "local_street": "Rue du Puits",
                "identifier": "puits",
            }
        )
        cls.local_street_namur = cls.env["address.local.street"].create(
            {
                "local_zip": "5000",
                "local_street": "Rue du Moulin",
                "identifier": "moulin",
            }
        )
        cls.federal = cls.env.ref("mozaik_structure.int_instance_01")
        cls.omar_sy = cls.env["res.partner"].create(
            {
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omarsy@test.com",
            }
        )

    def test_autoval_failed_no_autoval_type(self):
        mr = self.mr_model.create(
            {
                "autovalidation_type": False,
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
        failure_reason = mr._auto_validate(True)
        self.assertFalse(mr.partner_id)
        self.assertEqual("confirm", mr.state)
        self.assertEqual(
            failure_reason,
            "No autovalidation (neither complete or partial) selected on the MR.",
        )

    def test_light_autoval_failed_explicit_skip(self):
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
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
        failure_reason = mr._auto_validate(False)
        self.assertFalse(mr.partner_id)
        self.assertEqual("confirm", mr.state)
        self.assertEqual(failure_reason, "Auto validation manually set to false")

    def test_light_autoval_failed_no_email(self):
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "DUJARDIN",
                "firstname": "Jean",
                "gender": "male",
                "street_man": False,
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "request_type": "m",
            }
        )
        failure_reason = mr._auto_validate(True)
        self.assertFalse(mr.partner_id)
        self.assertEqual("confirm", mr.state)
        self.assertEqual(failure_reason, "Email is required for light autovalidation.")

    def test_light_autoval_failed_several_matched_partners(self):
        self.env["res.partner"].create(
            [
                {
                    "lastname": "Dumoulin",
                    "firstname": "Jean",
                    "email": "jd@test.com",
                },
                {
                    "lastname": "Dupont",
                    "firstname": "Jean",
                    "email": "jd@test.com",
                },
            ]
        )
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "DUJARDIN",
                "firstname": "Jean",
                "email": "jd@test.com",
                "gender": "male",
                "street_man": False,
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "request_type": "m",
            }
        )
        failure_reason = mr._auto_validate(True)
        self.assertFalse(mr.partner_id)
        self.assertEqual("confirm", mr.state)
        self.assertEqual(
            failure_reason,
            "Several partners found with email 'jd@test.com'. Light autovalidation failed.",
        )

    def test_light_autoval_involvements(self):
        """
        Check light auto-validation validates the involvements
        """
        ic_1 = self.env["partner.involvement.category"].create(
            {
                "name": "First IC",
            }
        )
        ic_2 = self.env["partner.involvement.category"].create(
            {
                "name": "Second IC",
            }
        )
        inv_effective_time = datetime(2026, 2, 16, 13)
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omarsy@test.com",
                "gender": "male",
                "street_man": False,
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "request_type": "m",
                "involvement_category_ids": [(4, ic_1.id), (4, ic_2.id)],
                "effective_time": inv_effective_time,
            }
        )
        failure_reason = mr._auto_validate(True)
        self.assertFalse(failure_reason)
        self.assertTrue(mr.light_mr_id)
        self.assertEqual(mr.state, "light_autoval")
        self.assertFalse(mr.active)
        self.assertEqual(mr.light_mr_id.state, "validate")
        self.assertFalse(mr.light_mr_id.active)
        self.assertEqual(mr.light_mr_id.partner_id, self.omar_sy)
        self.assertEqual(len(self.omar_sy.partner_involvement_ids), 2)
        self.assertEqual(
            set(
                self.omar_sy.partner_involvement_ids.mapped(
                    "involvement_category_id.id"
                )
            ),
            {ic_1.id, ic_2.id},
        )
        self.assertEqual(
            self.omar_sy.partner_involvement_ids[0].effective_time, inv_effective_time
        )
        self.assertEqual(
            self.omar_sy.partner_involvement_ids[1].effective_time, inv_effective_time
        )

    def test_light_autoval_indexation_comments(self):
        competency_1 = self.env["thesaurus.term"].create({"name": "Competency 1"})
        competency_2 = self.env["thesaurus.term"].create({"name": "Competency 2"})
        interest_1 = self.env["thesaurus.term"].create({"name": "Interest 1"})
        interest_2 = self.env["thesaurus.term"].create({"name": "Interest 2"})
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "Omar",
                "firstname": "Sy",
                "partner_id": self.omar_sy.id,
                "email": "omarsy@test.com",
                "gender": "male",
                "request_type": "m",
                "indexation_comments": "Comment",
            }
        )
        mr.write(
            {
                "competency_ids": [(4, competency_1.id), (4, competency_2.id)],
                "interest_ids": [(4, interest_1.id), (4, interest_2.id)],
            }
        )
        # NB: Here we validate without pre-process because the pre-process mechanism
        # tends to clean interest&competency values. There exists a mechanism that
        # protects the values in this case, but avoiding pre-process for this specific
        # case is easier
        failure_reason = mr.with_context(mode="no_pre_process")._auto_validate(True)
        self.assertFalse(failure_reason)
        self.assertTrue(mr.light_mr_id)
        self.assertEqual(mr.state, "light_autoval")
        self.assertFalse(mr.active)
        self.assertEqual(mr.light_mr_id.state, "validate")
        self.assertFalse(mr.light_mr_id.active)
        self.assertEqual(mr.light_mr_id.partner_id, self.omar_sy)
        self.assertEqual(len(self.omar_sy.competency_ids), 2)
        self.assertEqual(
            set(self.omar_sy.competency_ids.ids), {competency_1.id, competency_2.id}
        )
        self.assertEqual(len(self.omar_sy.interest_ids), 2)
        self.assertEqual(
            set(self.omar_sy.interest_ids.ids), {interest_1.id, interest_2.id}
        )
        self.assertEqual(self.omar_sy.indexation_comments, "Comment")

    # def test_light_autoval_payment(self):
    #     # TODO depending on Ecolo's answer
    #     self.assertTrue(False)

    def test_light_autoval_new_partner_partial_address(self):
        """
        Check that new partner is created with partial address
        """
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "DUJARDIN",
                "firstname": "Jean",
                "email": "jd@test.com",
                "gender": "male",
                "street_man": False,
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "request_type": "m",
            }
        )
        last_id = self.env["res.partner"].search([], order="id desc", limit=1).id
        failure_reason = mr._auto_validate(True)
        self.assertFalse(failure_reason)
        self.assertTrue(mr.light_mr_id)
        partner = mr.light_mr_id.partner_id
        self.assertGreater(partner.id, last_id)
        self.assertEqual(partner.lastname, "Dujardin")
        self.assertEqual(partner.firstname, "Jean")
        self.assertEqual(partner.email, "jd@test.com")
        self.assertTrue(partner.address_address_id)
        self.assertEqual(partner.address_address_id.city_id, self.city_lg)

    def test_light_autoval_new_partner_full_address_local_street(self):
        """
        Light auto-validation failed because local street was given.
        """
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "DUJARDIN",
                "firstname": "Jean",
                "email": "jd@test.com",
                "gender": "male",
                "address_local_street_id": self.local_street.id,
                "number": "12",
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "request_type": "m",
            }
        )
        failure_reason = mr._auto_validate(True)
        self.assertEqual(
            failure_reason,
            "Some address fields have to be checked manually. Light autovalidation failed. ",
        )
        self.assertEqual(mr.state, "confirm")
        self.assertFalse(mr.light_mr_id)

    def test_light_autoval_new_partner_full_address_manual_street(self):
        """
        Light auto-validation failed because manual street was given.
        """
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "DUJARDIN",
                "firstname": "Jean",
                "email": "jd@test.com",
                "gender": "male",
                "street_man": "Rue du Puits",
                "number": "12",
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "request_type": "m",
            }
        )
        failure_reason = mr._auto_validate(True)
        self.assertEqual(
            failure_reason,
            "Some address fields have to be checked manually. Light autovalidation failed. ",
        )
        self.assertEqual(mr.state, "confirm")
        self.assertFalse(mr.light_mr_id)

    def test_light_autoval_matched_partner_no_address_mr_partial_address(self):
        """
        Matched partner has no address and MR has partial address
        -> Set partial address on partner
        """
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omarsy@test.com",
                "gender": "male",
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "request_type": "m",
            }
        )
        failure_reason = mr._auto_validate(True)
        self.assertFalse(failure_reason)
        self.assertTrue(mr.light_mr_id)
        self.assertEqual(mr.light_mr_id.state, "validate")
        self.assertTrue(self.omar_sy.address_address_id)
        self.assertEqual(self.omar_sy.address_address_id.city_id, self.city_lg)

    def test_light_autoval_matched_partner_no_address_mr_full_address(self):
        """
        Matched partner has no address and MR has full address -> Light autovalidation failed
        """
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omarsy@test.com",
                "gender": "male",
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "street_man": "Rue du Puits",
                "number": "12",
                "request_type": "m",
            }
        )
        failure_reason = mr._auto_validate(True)
        self.assertEqual(
            failure_reason,
            "Some address fields have to be checked manually. Light autovalidation failed. ",
        )
        self.assertEqual(mr.state, "confirm")
        self.assertFalse(mr.light_mr_id)

    def test_matched_partner_name_differs(self):
        """
        If matched partner but names differs, don't change name.
        """
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "Othername",
                "firstname": "Otherfirstname",
                "email": "omarsy@test.com",
                "gender": "male",
                "request_type": "m",
            }
        )
        failure_reason = mr._auto_validate(True)
        self.assertFalse(failure_reason)
        self.assertTrue(mr.light_mr_id)
        self.assertEqual(mr.state, "light_autoval")
        self.assertFalse(mr.active)
        self.assertEqual(mr.light_mr_id.state, "validate")
        self.assertFalse(mr.light_mr_id.active)
        self.assertEqual(mr.light_mr_id.partner_id, self.omar_sy)
        self.assertEqual(mr.light_mr_id.lastname, "Sy")
        self.assertEqual(mr.light_mr_id.firstname, "Omar")
        self.assertEqual(self.omar_sy.lastname, "Sy")
        self.assertEqual(self.omar_sy.firstname, "Omar")

    def test_matched_partner_email_differs(self):
        """
        Matched partner comes from partner_id field, but email differs
        -> Light auto-validation fails
        """
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "newemail_omarsy@test.com",
                "partner_id": self.omar_sy.id,
                "request_type": "m",
            }
        )
        failure_reason = mr._auto_validate(True)
        self.assertEqual(
            failure_reason,
            "Email on the matched partner and email on the membership request differ.",
        )
        self.assertEqual(mr.state, "confirm")
        self.assertFalse(mr.light_mr_id)

    def test_matched_partner_zip_differs(self):
        """
        Matched partner has an address, MR has a partial address, but zips differ.
        -> Light auto-validation fails.
        """
        self.omar_sy.address_address_id = self.env["address.address"].create(
            {
                "country_id": self.belgium.id,
                "city_id": self.city_namur.id,
                "address_local_street_id": self.local_street_namur.id,
                "number": "15",
            }
        )
        self.assertEqual(self.omar_sy.address_address_id.city_id, self.city_namur)
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omarsy@test.com",
                "gender": "male",
                "zip_man": "4000",
                "city_id": self.city_lg.id,
                "request_type": "m",
            }
        )
        failure_reason = mr._auto_validate(mr)
        self.assertEqual(
            failure_reason,
            f"Zip on the matched partner (ID: {self.omar_sy.id}) "
            f"and zip on the membership request differ. "
            f"Light autovalidation failed.",
        )
        self.assertEqual(mr.state, "confirm")
        self.assertFalse(mr.light_mr_id)

    def test_matched_partner_same_zip(self):
        """
        Matched partner has an address, MR has a partial address, but zips are equal.
        -> Light auto-validation succeeds.
        """
        self.omar_sy.address_address_id = self.env["address.address"].create(
            {
                "country_id": self.belgium.id,
                "city_id": self.city_namur.id,
                "address_local_street_id": self.local_street_namur.id,
                "number": "15",
            }
        )
        self.assertEqual(self.omar_sy.address_address_id.city_id, self.city_namur)
        mr = self.mr_model.create(
            {
                "autovalidation_type": "light",
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "omarsy@test.com",
                "gender": "male",
                "zip_man": "5000",
                "city_id": self.city_namur.id,
                "request_type": "m",
            }
        )
        failure_reason = mr._auto_validate(mr)
        self.assertFalse(failure_reason)
        self.assertEqual(mr.state, "light_autoval")
        self.assertTrue(mr.light_mr_id)
        self.assertEqual(mr.light_mr_id.state, "validate")
        # Address wasn't copied on light MR:
        self.assertFalse(mr.light_mr_id.zip_man)
        self.assertFalse(mr.light_mr_id.city_id)
        self.assertFalse(mr.light_mr_id.country_id)
