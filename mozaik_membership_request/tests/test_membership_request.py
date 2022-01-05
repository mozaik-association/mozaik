##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import date, datetime
from uuid import uuid4

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

MR_REQUIRED_AGE_KEY = "mr_required_age"


class TestMembership(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env.clear()
        self.partner_obj = self.env["res.partner"]

        self.mro = self.env["membership.request"]
        self.mrco = self.env["membership.request.change"]
        self.mrs = self.env["membership.state"]

        self.rec_partner = self.browse_ref("mozaik_address.res_partner_thierry")
        self.rec_partner_pauline = self.browse_ref(
            "mozaik_membership_request.res_partner_pauline"
        )
        self.rec_partner_jacques = self.browse_ref(
            "mozaik_membership.res_partner_jacques"
        )
        self.rec_address = self.browse_ref("mozaik_address.address_2")

        self.rec_mr_update = self.browse_ref(
            "mozaik_membership_request.membership_request_mp"
        )
        self.rec_mr_create = self.browse_ref(
            "mozaik_membership_request.membership_request_eh"
        )

    def test_pre_process(self):
        """
        Test that input values to create a ``membership.request``
        are found and matched with existing data
        """
        base_values = {
            "lastname": self.rec_partner.lastname,
            "firstname": self.rec_partner.firstname,
            "gender": self.rec_partner.gender,
            "day": 1,
            "month": 4,
            "year": 1985,
            "request_type": "s",
            "mobile": "061411232",
        }
        all_values = {
            "street": self.rec_address.address_local_street_id.local_street,
            "zip_man": self.rec_address.city_id.zipcode,
            "address_local_street_id": self.rec_address.address_local_street_id.id,
            "box": self.rec_address.box,
            "number": self.rec_address.number,
            "city_man": self.rec_address.city_id.name,
        }
        all_values.update(base_values)

        output_values = self.mro._pre_process(all_values)
        self.assertEqual(
            output_values.get("address_id", False),
            self.rec_address.id,
            "Should be the same address",
        )
        self.assertEqual(
            output_values.get("partner_id", False),
            self.rec_partner.id,
            "Should have the same partner",
        )
        output_values = self.mro._pre_process(base_values)
        self.assertEqual(
            output_values.get("int_instance_ids", False),
            self.rec_partner.int_instance_ids.ids,
            "Instance should be the instance of the partner",
        )

    def test_get_address_id(self):
        adrs = self.browse_ref("mozaik_address.address_3")
        adrs._compute_integral_address()  # recompute the technical_name
        address_local_street_id = (
            adrs.address_local_street_id and adrs.address_local_street_id.id
        )
        city_id = adrs.city_id and adrs.city_id.id
        country_id = adrs.country_id and adrs.country_id.id
        technical_name = self.mro.get_technical_name(
            address_local_street_id,
            city_id,
            adrs.number,
            adrs.box,
            adrs.city_man,
            adrs.street_man,
            adrs.zip_man,
            country_id,
        )
        waiting_adrs_ids = self.env["address.address"].search(
            [("technical_name", "=", technical_name)]
        )
        waiting_adrs_id = -1
        if waiting_adrs_ids:
            waiting_adrs_id = waiting_adrs_ids[0]
        self.assertEqual(adrs, waiting_adrs_id, "Address id Should be the same")

    def test_voluntaries(self):
        """
        * Test the validate process and check for
        ** regional_voluntary and local_only
        """
        mr_obj = self.env["membership.request"]

        vals = {
            "firstname": "Virginie",
            "lastname": "EFIRA",
        }

        # create and validate a membership request
        mr = mr_obj.create(vals)
        mr.validate_request()
        partner = mr.partner_id
        self.assertFalse(partner.local_only)

        # create membership request from the partner
        mr_id = partner.button_modification_request()["res_id"]
        mr = mr_obj.browse([mr_id])

        vals = {
            "local_only": True,
        }
        mr.write(vals)
        self.assertTrue(mr.local_only)

        # validate the request
        mr.validate_request()
        self.assertTrue(partner.local_only)

        # create membership request from the partner
        mr_id = partner.button_modification_request()["res_id"]
        mr = mr_obj.browse([mr_id])

        vals = {
            "request_type": "s",
        }
        mr.write(vals)
        mr.onchange_partner_id()
        self.assertFalse(mr.local_only)

        # validate the request
        mr.validate_request()
        # updated because we go from without membership to supporter
        self.assertFalse(partner.local_only)

        # create membership request from the partner
        mr_id = partner.button_modification_request()["res_id"]
        mr = mr_obj.browse([mr_id])

        vals = {
            "request_type": "m",
        }
        vals["regional_voluntary"] = True
        mr.write(vals)
        mr.onchange_partner_id()
        self.assertTrue(mr.regional_voluntary)

        # validate the request
        mr.validate_request()
        # not updated because of the membership state
        self.assertFalse(partner.regional_voluntary)

        return

    def test_validate_request(self):
        """
        * Test the validate process with an update and check for
        ** firstname
        ** email
        ** mobile
        ** amount and reference
        ** not loss of original birthdate (mr do never reset fields)
        * Test the validate process with a create and check that
            relations are created
        """
        partner_obj = self.env["res.partner"]
        congo = self.ref("base.cd")

        # 1. partner to update
        mr = self.rec_mr_update
        partner = mr.partner_id

        # change some properties
        vals = {
            "phone": "444719",
            "number": "007",
            "box": "jb",
            "amount": 7.0,
            "reference": "+++555/2017/00055+++",
            "nationality_id": congo,
        }

        # update the membership request
        mr.write(vals)
        mr.onchange_other_address_componants()
        mr.onchange_technical_name()
        mr.onchange_phone()
        # validate the membership request
        mr.validate_request()

        self.assertEqual(mr.firstname, partner.firstname)
        self.assertEqual(mr.email, partner.email)
        self.assertEqual(mr.mobile, partner.mobile)
        self.assertTrue(partner.birthdate_date)
        self.assertEqual(mr.force_int_instance_id.id, partner.int_instance_ids.id)
        # self.assertEqual(mr.reference, partner.reference) TODO
        # self.assertEqual(mr.amount, partner.amount)
        self.assertEqual(mr.nationality_id, partner.nationality_id)

        # 2. partner to create
        mr = self.rec_mr_create
        mr.validate_request()

        created_partner_ids = partner_obj.search(
            [
                ("firstname", "=", mr.firstname),
                ("lastname", "=", mr.lastname),
                ("birthdate_date", "=", fields.Date.to_string(mr.birthdate_date)),
            ]
        )
        self.assertEqual(len(created_partner_ids), 1)
        # test address and phone
        address_ids = self.env["address.address"].search(
            [("technical_name", "=", mr.technical_name)]
        )
        self.assertEqual(len(address_ids), 1)

    def test_state_default_get(self):
        """
        Test the default state of `membership.state`
        'without_membership' is used as technical state

        Test default state with another default_state
        """
        mrs = self.mrs

        uniq_code_membership = mrs._get_default_state()
        self.assertEqual(
            "without_membership",
            uniq_code_membership.code,
            "Code should be without_membership",
        )

        code = "%s" % uuid4()
        mrs.create({"name": "test_state", "code": code})
        uniq_code_membership = mrs._get_default_state(default_state=code)
        self.assertEqual(code, uniq_code_membership.code, "Code should be %s" % code)

    def test_track_changes(self):
        """
        Test to valid tracks changes method to detect differences
        between modification request and partner data
        """

        request = self.rec_mr_update
        request.write(
            {
                "regional_voluntary": True,
                "local_only": True,
            }
        )

        def get_changes():
            changes = {}
            for change in request.change_ids:
                changes[change.field_name] = (change.old_value, change.new_value)
            return changes

        changes = get_changes()
        self.assertIn("Firstname", changes)
        self.assertIn("Mobile", changes)
        self.assertIn("Gender", changes)
        self.assertIn("Email", changes)
        self.assertNotIn("Birth Date", changes)
        self.assertIn("Regional Voluntary", changes)

        self.assertEqual(changes["Name"][0], "Pauline")
        self.assertEqual(
            changes["Name"][1], "Marois"
        )  # lastname was formatted at creation
        self.assertFalse(changes["Mobile"][0])
        # self.assertEqual(changes['Mobile'][1], '+32 475 45 12 32') TODO only works first time?
        self.assertFalse(changes["Gender"][0])
        self.assertEqual(changes["Gender"][1], "Female")
        self.assertFalse(changes["Email"][0])
        self.assertEqual(changes["Email"][1], "pauline_marois@gmail.com")
        self.assertEqual(changes["Regional Voluntary"][0], "No")
        self.assertEqual(changes["Regional Voluntary"][1], "Yes")
        self.assertEqual(changes["Local Only"][0], "No")
        self.assertEqual(changes["Local Only"][1], "Yes")

        # change main address of the partner
        vals = {
            "country_id": self.ref("base.be"),
            "zip_man": "4000",
            "city_man": u"Liège",
            "street_man": "Place St Lambert",
            "number": "7",
        }
        adr_id = self.env["address.address"].create(vals)
        request.partner_id.address_address_id = adr_id
        request.write({"lastname": "Test"})
        changes = get_changes()
        self.assertIn("Name", changes)
        self.assertIn("City", changes)
        self.assertIn("Reference Street", changes)
        self.assertIn("Number", changes)
        self.assertEqual(changes["Name"][0], "Pauline")
        self.assertEqual(changes["Name"][1], "Test")
        self.assertEqual(changes["City"][0], "Liège")
        self.assertEqual(changes["City"][1], "Oreye")
        self.assertEqual(changes["Reference Street"][0], "Place St Lambert")
        self.assertEqual(changes["Reference Street"][1], "Rue Louis Maréchal")
        self.assertEqual(changes["Number"][0], "7")
        self.assertEqual(changes["Number"][1], "6")

        # change address components of the request
        vals = {
            "country_id": self.ref("base.ma"),
            "zip_man": "45000",
            "city_man": "Ouarzazate",
            "street_man": "rue du souk",
            "number": "47",
            "box": False,
        }
        request.write(vals)
        request.onchange_country_id()
        request.onchange_city_id()
        request.onchange_other_address_componants()
        request.onchange_technical_name()
        changes = get_changes()
        self.assertIn("Country", changes)
        self.assertIn("Zip", changes)
        self.assertIn("City (Manual)", changes)
        self.assertIn("Street", changes)
        self.assertIn("Number", changes)
        self.assertEqual(changes["Country"][0], "Belgium")
        self.assertEqual(changes["Country"][1], "Morocco")
        self.assertEqual(changes["Zip"][0], "4000")
        self.assertEqual(changes["Zip"][1], "45000")
        self.assertEqual(changes["City (Manual)"][0], u"Liège")
        self.assertEqual(changes["City (Manual)"][1], "Ouarzazate")
        self.assertEqual(changes["Street"][0], "Place St Lambert")
        self.assertEqual(changes["Street"][1], "rue du souk")
        self.assertEqual(changes["Number"][0], "7")
        self.assertEqual(changes["Number"][1], "47")

        # reset country on request
        request.write({"country_id": False})
        changes = get_changes()
        self.assertNotIn("City (Manual)", changes)
        self.assertNotIn("Zip", changes)
        self.assertNotIn("City (Manual)", changes)
        self.assertNotIn("Reference Street", changes)
        self.assertNotIn("Street", changes)
        self.assertNotIn("Street2", changes)
        self.assertNotIn("Number", changes)
        self.assertNotIn("Box", changes)
        self.assertNotIn("Sequence", changes)

    def test_age_computation(self):
        """
        Check value of age depending of the birth_date
        """
        age = 10
        birth_date = datetime.strftime(
            date.today() - relativedelta(years=age), DEFAULT_SERVER_DATE_FORMAT
        )
        vals = {
            "birthdate_date": birth_date,
        }
        mr_id = self.env.ref("mozaik_membership_request.membership_request_mp")
        mr_copy = mr_id.copy()
        mr_copy.write(vals)
        self.assertEqual(mr_copy.age, age, "Should be the same age")

    def test_required_age(self):
        mr_obj = self.env["membership.request"]
        minage = int(
            self.env["ir.config_parameter"].get_param(MR_REQUIRED_AGE_KEY, default=16)
        )
        name = "Test"
        d = date.today() - relativedelta(years=minage) + relativedelta(days=1)
        vals = {
            "lastname": name,
            "firstname": name,
            "state": "confirm",
            "gender": "male",
            "day": d.day,
            "month": d.month,
            "year": d.year,
            "request_type": "m",
        }
        mr = mr_obj.with_context(mode="ws").create(vals)
        self.assertRaises(ValidationError, mr.validate_request)

        d = date.today() - relativedelta(years=minage)
        vals = {
            "day": d.day,
            "month": d.month,
            "year": d.year,
        }
        mr.write(vals)
        mr.onchange_partner_component()
        mr.validate_request()
        self.assertEqual(mr.state, "validate", "Validation should work")
