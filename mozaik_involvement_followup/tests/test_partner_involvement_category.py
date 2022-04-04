# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase
from odoo.tools.misc import mute_logger


class TestPartnerInvolvementCategory(SavepointCase):
    def test_involvement_category_integrity_1(self):
        # create a category with negative deadline rule: NOK
        with self.assertRaises(ValidationError), mute_logger("odoo.sql_db"):
            self.env["partner.involvement.category"].create(
                {
                    "name": "Le tour du monde en 80 jours",
                    "nb_deadline_days": -80,
                    "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
                }
            )

    def test_involvement_category_integrity_2(self):
        mc_id = self.ref("mozaik_mandate.mc_secretaire_regional")
        # create a category without deadline rule but with a mandate: NOK
        with self.assertRaises(ValidationError), mute_logger("odoo.sql_db"):
            self.env["partner.involvement.category"].create(
                {
                    "name": "Le tour du monde en 80 jours",
                    "nb_deadline_days": 0,
                    "mandate_category_id": mc_id,
                    "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
                }
            )

    def test_involvement_category_onchange_deadline_rule(self):
        mc_id = self.ref("mozaik_mandate.mc_secretaire_regional")
        vals = {
            "name": "Blanche neige et les 7 nains",
            "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
        }
        ic = self.env["partner.involvement.category"].create(vals)
        vals = {
            "name": "Le tour du monde en 80 jours",
            "nb_deadline_days": 0,
            "mandate_category_id": mc_id,
            "involvement_category_ids": [(6, 0, [ic.id])],
            "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
        }
        cat = self.env["partner.involvement.category"].new(vals)
        # change deadline rule to null
        cat._onchange_nb_deadline_days()
        # mandate category and follow-up categories must be false
        self.assertFalse(cat.mandate_category_id)
        self.assertFalse(cat.involvement_category_ids)
        return

    def test_involvement_category_followup_constrains(self):
        vals = {
            "name": "Blanche neige et les 7 nains",
            "nb_deadline_days": 1,
            "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
        }
        ic3 = self.env["partner.involvement.category"].create(vals)
        vals = {
            "name": "Blanche neige et les 7 vilains",
            "nb_deadline_days": 1,
            "involvement_category_ids": [(6, 0, [ic3.id])],
            "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
        }
        ic2 = self.env["partner.involvement.category"].create(vals)
        vals = {
            "name": "Blanche neige et les 7 mains",
            "nb_deadline_days": 1,
            "involvement_category_ids": [(6, 0, [ic2.id])],
            "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
        }
        ic1 = self.env["partner.involvement.category"].create(vals)
        # make a recursion loop through involvement_category_ids => NOK
        self.assertRaises(
            ValidationError, ic3.write, {"involvement_category_ids": [(6, 0, [ic1.id])]}
        )
        ic3.involvement_category_ids = False
        # make ic3 a petition => NOK
        self.assertRaises(ValidationError, ic3.write, {"involvement_type": "petition"})
        ic3.involvement_type = False
        # make ic3 a voluntary => OK
        ic3.involvement_type = "voluntary"
        # make ic1 a petition => OK
        ic1.write({"involvement_type": "petition"})
        return

    def test_followup(self):
        wizard = self.env["partner.involvement.followup.wizard"]
        follower = self.env.user.partner_id
        vals = {
            "name": "Blanche neige et les 7 nains",
            "nb_deadline_days": 1,
            "message_follower_ids": [(6, 0, [follower.id])],
            "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
        }
        ic3 = self.env["partner.involvement.category"].create(vals)
        vals = {
            "name": "Blanche neige et les 7 vilains",
            "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
        }
        ic2 = self.env["partner.involvement.category"].create(vals)
        vals = {
            "name": "Blanche neige et les 7 mains",
            "nb_deadline_days": 1,
            "involvement_category_ids": [(6, 0, [ic3.id, ic2.id])],
            "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
        }
        ic1 = self.env["partner.involvement.category"].create(vals)
        # create a partner and an involvement
        vals = {
            "name": "Blanche neige",
        }
        partner = self.env["res.partner"].create(vals)
        involvement = self.env["partner.involvement"].create(
            {
                "partner_id": partner.id,
                "involvement_category_id": ic1.id,
            }
        )
        # create a follow-up wizard and execute it
        # 1. just finish the followup
        wiz = wizard.with_context(active_id=involvement.id).create({"followup": "done"})
        # test domain of next_category_ids field
        dom = wiz._next_category_ids_domain()
        self.assertEqual({ic3.id, ic2.id}, set(dom[0][2]))
        wiz.doit()
        self.assertTrue(involvement.effective_time)
        self.assertEqual("done", involvement.state)
        # create another partner and an involvement
        vals = {
            "name": "Cendrillon",
        }
        partner = self.env["res.partner"].create(vals)
        involvement = self.env["partner.involvement"].create(
            {
                "partner_id": partner.id,
                "involvement_category_id": ic1.id,
            }
        )
        ic1.nb_deadline_days = 4
        # create a follow-up wizard and execute it
        # 2. additional delay
        wiz = wizard.with_context(active_id=involvement.id).create(
            {"followup": "delay"}
        )
        wiz.doit()
        deadline = (date.today() + relativedelta(days=4)).strftime("%Y-%m-%d")
        self.assertEqual(deadline, involvement.deadline.strftime("%Y-%m-%d"))
        # create another partner and an involvement
        vals = {
            "name": "Pocahontas",
        }
        partner = self.env["res.partner"].create(vals)
        involvement = self.env["partner.involvement"].create(
            {
                "partner_id": partner.id,
                "involvement_category_id": ic1.id,
            }
        )
        # create a follow-up wizard and execute it
        # 3. start new follow-up
        wiz = wizard.with_context(active_id=involvement.id).create(
            {
                "followup": "continue",
                "next_category_ids": [(6, 0, ic1.involvement_category_ids.ids)],
            }
        )
        wiz.doit()
        # check for new followup
        self.assertEqual(
            ic1 + ic1.involvement_category_ids,
            partner.partner_involvement_ids.mapped("involvement_category_id"),
        )
        # check for followers
        self.assertEqual(
            follower,
            partner.partner_involvement_ids.filtered(
                lambda s, ic=ic3: s.involvement_category_id == ic
            )
            .mapped("message_follower_ids")
            .partner_id,
        )
        self.assertTrue(
            partner.partner_involvement_ids.filtered(
                lambda s, ic=ic2: s.involvement_category_id == ic
            ).mapped("message_follower_ids")
        )

        return
