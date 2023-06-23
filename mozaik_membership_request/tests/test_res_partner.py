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

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.tests.common import TransactionCase


class TestPartner(TransactionCase):
    def setUp(self):
        super().setUp()

        self.mr_obj = self.env["membership.request"]
        self.partner_obj = self.env["res.partner"]
        self.ms_obj = self.env["membership.state"]
        self.ml_obj = self.env["membership.line"]
        self.prd_obj = self.env["product.template"]
        self.imd_obj = self.env["ir.model.data"]

        self.partner1 = self.browse_ref("mozaik_address.res_partner_thierry")

        self.partner2 = self.browse_ref("mozaik_membership.res_partner_fgtb")

        self.user_model = self.env["res.users"]
        self.partner_jacques_id = self.ref("mozaik_membership.res_partner_jacques")

    def test_button_modification_request(self):
        """
        Check that a `membership.request` object is well created with
        the datas of the giving partner.
        test raise if partner does not exist
        """
        mr_obj, partner = self.mr_obj, self.partner1
        fr = self.ref("base.fr")
        partner.write(
            {
                "regional_voluntary": True,
                "local_only": True,
                "nationality_id": fr,
            }
        )
        res = partner.button_modification_request()
        mr = mr_obj.browse(res["res_id"])
        int_instance_id = partner.int_instance_ids or False
        birthdate_date = partner.birthdate_date
        day = False
        month = False
        year = False
        if partner.birthdate_date:
            day = partner.birthdate_date.day
            month = partner.birthdate_date.month
            year = partner.birthdate_date.year
        self.assertEqual(mr.membership_state_id, partner.membership_state_id)
        self.assertEqual(mr.result_type_id, partner.membership_state_id)
        self.assertEqual(
            mr.identifier,
            partner.identifier,
            "[memb.req.]\
        identifier should be the same that [partner]identifier ",
        )
        self.assertEqual(
            mr.lastname,
            partner.lastname,
            "[memb.req.]lastname\
        should be the same that [partner]lastname ",
        )
        self.assertEqual(
            mr.firstname,
            partner.firstname,
            "[memb.req.]\
        firstname should be the same that [partner]firstname ",
        )
        self.assertEqual(
            mr.gender,
            partner.gender,
            "[memb.req.]gender should \
        be the same that [partner]gender ",
        )
        self.assertEqual(
            mr.birthdate_date,
            birthdate_date,
            "[memb.req.]birthdate_date \
        should be the same that [partner]birthdate_date ",
        )
        self.assertEqual(
            mr.day,
            day and int(day),
            "[memb.req.]day should be \
        the same that [partner]day ",
        )
        self.assertEqual(
            mr.month,
            month and int(month),
            "[memb.req.]month \
        should be the same that [partner]month ",
        )
        self.assertEqual(
            mr.year,
            year and int(year),
            "[memb.req.]year should\
        be the same that [partner]year ",
        )
        self.assertEqual(
            mr.is_update,
            True,
            "[memb.req.]is_update should be \
        True",
        )
        self.assertEqual(
            mr.int_instance_ids and mr.int_instance_ids.ids or False,
            int_instance_id and int_instance_id.ids,
            "[memb.req.]int_instance_id should be the same that \
                         [partner]int_instance_id ",
        )
        self.assertEqual(
            mr.interest_ids or [[6, False, []]],
            [
                [
                    6,
                    False,
                    partner.interest_ids
                    and [interest.id for interest in partner.interest_ids]
                    or [],
                ]
            ],
            "[memb.req.]interest_ids should be the same \
                         that [partner]interest_ids ",
        )
        self.assertEqual(
            mr.partner_id and mr.partner_id.id,
            partner.id,
            "[memb.req.]partner_id should be the same that \
                         [partner]partner_id ",
        )
        self.assertEqual(
            mr.competency_ids or [[6, False, []]],
            [
                [
                    6,
                    False,
                    partner.competency_ids
                    and [competence.id for competence in partner.competency_ids]
                    or [],
                ]
            ],
            "[memb.req.]competency_ids should be the same \
                         that [partner]competency_idss ",
        )
        # Selection fields are empty
        self.assertFalse(mr.local_voluntary)
        self.assertFalse(mr.regional_voluntary)
        self.assertFalse(mr.local_only)
        self.assertFalse(mr.national_voluntary)
        self.assertEqual(mr.nationality_id, partner.nationality_id)

    def test_accept_member_committee(self):
        """
        Testing ir_cron_accept_membership_committee cron.

        1. Harry is a member committee, date_from is yesterday.
        -> Run the "Accept member committee" cron: nothing happens
        2. Change date_from, it is now 2 months ago. But tick
        suspend_member_auto_validation
        -> Run the "Accept member committee" cron: nothing happens
        3. Untick suspend_member_auto_validation
        -> Run the "Accept member committee" cron: Harry became a member
        """
        harry = self.env["res.partner"].create({"name": "Harry Potter"})
        self.env["add.membership"].create(
            {
                "partner_id": harry.id,
                "int_instance_id": self.env.ref("mozaik_structure.int_instance_01").id,
                "state_id": self.env.ref("mozaik_membership.member_committee").id,
                "date_from": date.today() - relativedelta(days=1),
            }
        ).action_add()
        self.assertEqual(harry.membership_state_code, "member_committee")
        # 1.
        self.env["membership.line"].cron_accept_member_committee()
        self.assertEqual(harry.membership_state_code, "member_committee")
        # 2.
        harry.suspend_member_auto_validation = True
        harry.membership_line_ids[0].date_from = date.today() - relativedelta(months=2)
        self.env["membership.line"].cron_accept_member_committee()
        self.assertEqual(harry.membership_state_code, "member_committee")
        # 3.
        harry.suspend_member_auto_validation = False
        self.env["membership.line"].cron_accept_member_committee()
        self.assertEqual(harry.membership_state_code, "member")
