# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo.exceptions import AccessError


class TestIrRule(SavepointCase):

    def test_ir_rule(self):
        ir_rule = self.env["ir.rule"]
        res_users = self.env["res.users"]
        ir_model = self.env["ir.model"]

        model = ir_model.search([("model", "=", "res.users")])
        ir_rule.search([("model_id", "=", model.id)]).unlink()

        ir_rule.create({
            "name": "test",
            "model_id": model.id,
            "domain_force": "[('company_ids','child_of',user.company_ids.ids)]"
        })

        user1 = res_users.create({
            "name": "ir_rule_test1",
            "login": "ir_rule_test1",
        })
        user2 = res_users.create({
            "name": "ir_rule_test2",
            "login": "ir_rule_test2",
        })

        # can read
        self.assertEqual(user2.sudo(user=user1).name, "ir_rule_test2")

        user1.company_ids = False
        user2.invalidate_cache()
        ir_rule.clear_caches()
        # since user1.company_ids.ids is a empty list, it cannot read
        # the user2 attribute
        self.assertRaises(AccessError, getattr, user2.sudo(user=user1), "name")
