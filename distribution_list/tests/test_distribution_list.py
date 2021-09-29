# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from uuid import uuid4

from odoo import exceptions
from odoo.tests.common import SavepointCase


class TestDistributionList(SavepointCase):
    def setUp(self):
        super(TestDistributionList, self).setUp()
        self.partner_obj = self.env["res.partner"]
        self.dist_list_obj = self.env["distribution.list"]
        self.dist_list_line_obj = self.env["distribution.list.line"]
        self.first_user = self.env.ref("distribution_list.first_user")
        self.second_user = self.env.ref("distribution_list.second_user")
        self.partner_model = self.env.ref("base.model_res_partner")
        self.partner_id_field = self.env.ref("base.field_res_partner__id")
        self.parent_id_field = self.env.ref("base.field_res_partner__parent_id")
        # inactive RR define elsewhere (for test db reusing purpose)
        model_ids = [
            self.ref("distribution_list.model_distribution_list"),
            self.ref("base.model_res_partner"),
        ]
        rules = self.env["ir.rule"].search([("model_id", "in", model_ids)])
        rules -= self.browse_ref("distribution_list.distribution_list_company_rule")
        rules.toggle_active()

    def test_confidentiality_distribution_list(self):
        """
        This function check access rights/rules for these models:
        - distribution.list
        - distribution.list.line
        A user can see his distribution list (and related lines) of his
        company but not others
        :return:
        """
        distri_list_obj = self.dist_list_obj
        user_creator = self.first_user
        user_no_access = self.second_user
        # create distribution_list_line and distribution_list with the first
        # user
        distri_list_obj = distri_list_obj.with_user(user_creator.id)
        dist_list_line_values = {
            "name": "employee",
            "domain": "[('employee', '=', True)]",
            "src_model_id": self.partner_model.id,
            "exclude": False,
            "bridge_field_id": self.partner_id_field.id,
        }
        distribution_list = distri_list_obj.create(
            {
                "name": "tee meeting",
                "company_id": user_creator.company_id.id,
                "dst_model_id": self.partner_model.id,
                "to_include_distribution_list_line_ids": [
                    (0, False, dist_list_line_values),
                ],
            }
        )
        distribution_list_line = distribution_list.to_include_distribution_list_line_ids
        self.assertEqual(len(distribution_list_line), 1)
        with self.assertRaises(exceptions.AccessError):
            distribution_list_line.with_user(user_no_access.id).read()
        self.assertEqual(len(distribution_list), 1)
        with self.assertRaises(exceptions.AccessError):
            distribution_list.with_user(user_no_access.id).read()
        return

    def test_compute_distribution_list_ids(self):
        """

        :return:
        """
        partner_obj = self.partner_obj
        distri_list_obj = self.dist_list_obj
        distri_list_line_obj = self.dist_list_line_obj

        user_creator = self.first_user
        partner_obj = partner_obj.with_user(user_creator.id)
        customer = partner_obj.create(
            {
                "active": True,
                "type": "contact",
                "is_company": False,
                "lang": "en_US",
                "child_ids": [],
                "user_ids": [],
                "name": "customer",
                "category_id": [[6, False, []]],
                "company_id": user_creator.company_id.id,
            }
        )

        supplier = partner_obj.create(
            {
                "active": True,
                "type": "contact",
                "is_company": False,
                "lang": "en_US",
                "child_ids": [],
                "user_ids": [],
                "name": "supplier",
                "category_id": [[6, False, []]],
                "company_id": user_creator.company_id.id,
            }
        )

        # create distribution_list_line and distribution_list with the first
        # user
        partner_obj = self.partner_model
        distri_list_line_obj = distri_list_line_obj.with_user(user_creator.id)
        distri_list_obj = distri_list_obj.with_user(user_creator.id)

        distribution_list = distri_list_obj.create(
            {
                "name": str(uuid4()),
                "company_id": user_creator.company_id.id,
                "dst_model_id": partner_obj.id,
            }
        )
        line1 = distri_list_line_obj.create(
            {
                "name": str(uuid4()),
                "src_model_id": partner_obj.id,
                "company_id": user_creator.company_id.id,
                "distribution_list_id": distribution_list.id,
                "bridge_field_id": self.partner_id_field.id,
                "domain": "[('company_id','=',"
                + str(user_creator.company_id.id)
                + ")]",
            }
        )
        line2 = distri_list_line_obj.create(
            {
                "name": "employee_2",
                "src_model_id": partner_obj.id,
                "company_id": user_creator.company_id.id,
                "distribution_list_id": distribution_list.id,
                "bridge_field_id": self.partner_id_field.id,
                "domain": "[('company_id','=',"
                + str(user_creator.company_id.id)
                + ")]",
            }
        )

        distribution_list_exclusion = distri_list_obj.create(
            {
                "name": "tee meeting 2",
                "company_id": user_creator.company_id.id,
                "dst_model_id": partner_obj.id,
            }
        )
        line1.copy(
            {
                "distribution_list_id": distribution_list_exclusion.id,
                "exclude": True,
                "name": str(uuid4()),
            }
        )
        line2.copy(
            {
                "distribution_list_id": distribution_list_exclusion.id,
                "exclude": True,
                "name": str(uuid4()),
            }
        )

        targets = distribution_list._get_target_from_distribution_list()
        self.assertIn(customer.id, targets.ids)
        self.assertIn(supplier.id, targets.ids)

        targets = distribution_list_exclusion._get_target_from_distribution_list()
        self.assertNotIn(customer.id, targets.ids)
        self.assertNotIn(supplier.id, targets.ids)

        return

    def test_get_ids_from_distribution_list(self):
        """
        Will check that
        * calling `get_ids_from_distribution_list` with two distribution list
            that have two different model will raise `orm` exception
        * calling them with same model is OK
        """
        distribution_list_obj = self.dist_list_obj

        partner_model = self.partner_model

        distribution_list1 = distribution_list_obj.create(
            {
                "name": str(uuid4()),
                "dst_model_id": partner_model.id,
            }
        )
        distribution_list2 = distribution_list_obj.create(
            {
                "name": str(uuid4()),
                "dst_model_id": partner_model.id,
            }
        )
        will_succeed = distribution_list1 | distribution_list2
        for w in will_succeed:
            w._get_target_from_distribution_list()

    def test_complete_distribution_list(self):
        """
        1) Create 3 filters and 2 distribution lists
            dl one to_include: 1
            dl two to_include: 1
            dl two to_exclude: 1
        2) complete dl 1 with dl 2.
        3) Check that dl
            * has two filters ``to_include``
            * has one filter ``to_exclude``
        """
        dl_model = self.dist_list_obj
        dl_line_model = self.dist_list_line_obj
        dst_model_id = self.partner_model

        src_dist = dl_model.create(
            {
                "name": "src",
                "dst_model_id": dst_model_id.id,
            }
        )
        dl_line_model.create(
            {
                "name": str(uuid4()),
                "src_model_id": dst_model_id.id,
                "distribution_list_id": src_dist.id,
                "bridge_field_id": self.partner_id_field.id,
            }
        )
        dl_line_model.create(
            {
                "name": str(uuid4()),
                "src_model_id": dst_model_id.id,
                "distribution_list_id": src_dist.id,
                "exclude": True,
                "bridge_field_id": self.partner_id_field.id,
            }
        )

        trg_dist = dl_model.create(
            {
                "name": "trg",
                "dst_model_id": dst_model_id.id,
            }
        )
        dl_line_model.create(
            {
                "name": str(uuid4()),
                "src_model_id": dst_model_id.id,
                "distribution_list_id": trg_dist.id,
                "bridge_field_id": self.partner_id_field.id,
            }
        )
        trg_dist._complete_distribution_list(src_dist.ids)
        self.assertEqual(len(trg_dist.to_include_distribution_list_line_ids), 2)
        self.assertEqual(len(trg_dist.to_exclude_distribution_list_line_ids), 1)
        return

    def test_get_complex_distribution_list_ids(self):
        """
        Test that `get_complex_distribution_list_ids` return correct ids
        when using a context with
        * main_object_field
        * main_object_domain
        * alternative_object_field
        * alternative_object_domain
        * sort_by
        """
        partner_obj = self.partner_obj
        distri_list_obj = self.dist_list_obj
        distri_list_line_obj = self.dist_list_line_obj

        p9 = partner_obj.create(
            {
                "name": "p9",
                "company_id": self.browse_ref("base.main_company").id,
            }
        )
        p8 = partner_obj.create(
            {
                "name": "p8 more_filter filter_three",
                "parent_id": p9.id,
            }
        )
        partner_obj.create(
            {
                "name": "p7 more_filter filter_three",
                "parent_id": p8.id,
            }
        )

        p6 = partner_obj.create(
            {
                "name": "p6",
                "company_id": self.browse_ref("base.main_company").id,
            }
        )
        p5 = partner_obj.create(
            {
                "name": "p5",
                "company_id": self.browse_ref("base.main_company").id,
            }
        )
        p4 = partner_obj.create(
            {
                "name": "p4",
                "parent_id": p5.id,
            }
        )
        partner_obj.create(
            {
                "name": "p3 filter_two",
                "parent_id": p6.id,
            }
        )
        partner_obj.create(
            {
                "name": "p2 filter_one",
                "parent_id": p4.id,
            }
        )
        partner_obj.create(
            {
                "name": "p1 filter_one",
                "parent_id": p4.id,
            }
        )
        partner_model = self.partner_model
        dl = distri_list_obj.create(
            {
                "name": "get_complex_distribution_list_ids",
                "dst_model_id": partner_model.id,
            }
        )
        distri_list_line_obj.create(
            {
                "name": "filter_one",
                "domain": "[('name', 'ilike', 'filter_one')]",
                "src_model_id": partner_model.id,
                "distribution_list_id": dl.id,
                "bridge_field_id": self.parent_id_field.id,
            }
        )
        distri_list_line_obj.create(
            {
                "name": "filter_two",
                "domain": "[('name', 'ilike', 'filter_two')]",
                "src_model_id": partner_model.id,
                "distribution_list_id": dl.id,
                "bridge_field_id": self.parent_id_field.id,
            }
        )
        distri_list_line_obj.create(
            {
                "name": "filter_three",
                "domain": "[('name', 'ilike', 'filter_three')]",
                "src_model_id": partner_model.id,
                "distribution_list_id": dl.id,
                "bridge_field_id": self.parent_id_field.id,
            }
        )
        context = self.env.context.copy()
        context.update(
            {
                "main_object_field": "parent_id",
                "main_object_domain": [("name", "=", "p4")],
                "alternative_object_field": "company_id",
                "alternative_object_domain": [("parent_id", "=", False)],
                "sort_by": "name desc",
            }
        )
        mains, alternatives = dl.with_context(
            context
        )._get_complex_distribution_list_ids()
        self.assertEqual(p5, mains)
        self.assertEqual(self.browse_ref("base.main_company"), alternatives)

        context.pop("main_object_domain")
        mains, alternatives = dl.with_context(
            context
        )._get_complex_distribution_list_ids()
        self.assertEqual(p9 | p5, mains)

        context.update(
            {
                "main_object_domain": [("name", "=", "x23")],
            }
        )
        mains, alternatives = dl.with_context(
            context
        )._get_complex_distribution_list_ids()
        self.assertFalse(mains)

        context.pop("main_object_field")
        targets = dl.with_context(context)._get_target_from_distribution_list()
        mains, alternatives = dl.with_context(
            context
        )._get_complex_distribution_list_ids()
        self.assertEqual(mains, targets)
        return

    def test_duplicate_distribution_list_and_filters(self):
        """
        Test the duplication (copy) of a distribution list and a filter
        """
        distri_list_obj = self.dist_list_obj
        distri_list_line_obj = self.dist_list_line_obj
        user = self.first_user
        # create distribution_list_line and distribution_list
        partner_model = self.partner_model

        distribution_list = distri_list_obj.create(
            {
                "name": "tea meeting to copy",
                "dst_model_id": partner_model.id,
                "company_id": False,
            }
        )
        distri_list_line_obj.create(
            {
                "name": "employee to copy",
                "domain": "[('employee', '=', True)]",
                "src_model_id": partner_model.id,
                "distribution_list_id": distribution_list.id,
                "bridge_field_id": self.partner_id_field.id,
            }
        )

        distribution_list_copy = distribution_list.with_user(user.id).copy()
        self.assertEqual(
            distribution_list.dst_model_id.id, distribution_list_copy.dst_model_id.id
        )
        line_origin = distribution_list.to_include_distribution_list_line_ids
        line_cpy = distribution_list_copy.to_include_distribution_list_line_ids
        self.assertTrue(line_cpy)
        self.assertEqual(line_cpy.domain, line_origin.domain)
        self.assertEqual(line_cpy.exclude, line_origin.exclude)
        self.assertEqual(line_cpy.src_model_id.id, line_origin.src_model_id.id)
        return

    def test_mass_mailing(self):
        """
        Test that action is well returned with correct value required for
        a mass mailing
        """
        distribution_list_obj = self.dist_list_obj
        partner_model = self.partner_model

        dist_list = distribution_list_obj.create(
            {
                "name": str(uuid4()),
                "dst_model_id": partner_model.id,
            }
        )
        result = dist_list.mass_mailing()
        self.assertEqual(
            result.get("type"),
            "ir.actions.act_window",
            "Should be an ir.actions.act_window ",
        )
        self.assertEqual(
            result.get("res_model"),
            "mail.compose.message",
            "This mass mailing is made with mail composer",
        )
        # test context content
        context = result.get("context", {})
        self.assertEqual(
            context.get("default_composition_mode"),
            "mass_mail",
            "Mass mailing must be launch into mass_mail mode",
        )
        self.assertEqual(
            context.get("active_model"),
            "res.partner",
            "Active model must be the same that the distribution list",
        )
        self.assertEqual(
            context.get("default_distribution_list_id"),
            dist_list.id,
            "default_distribution_list_id must be the same that the "
            "distribution list's id",
        )
        return

    def test_action_show_result(self):
        """
        Test that action is well returned with correct value required for
        a `get_actions_from_domains`
        """
        distribution_list_obj = self.dist_list_obj
        partner_model = self.partner_model
        dist_list = distribution_list_obj.create(
            {
                "name": str(uuid4()),
                "dst_model_id": partner_model.id,
            }
        )
        result = dist_list.action_show_result()
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "res.partner")
        return
