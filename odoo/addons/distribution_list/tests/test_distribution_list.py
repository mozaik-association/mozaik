# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from uuid import uuid4
from odoo.tests.common import TransactionCase
from odoo import exceptions
from odoo.fields import first


class TestDistributionList(TransactionCase):

    def setUp(self):
        super(TestDistributionList, self).setUp()
        self.user_obj = self.env['res.users']
        self.partner_obj = self.env['res.partner']
        self.dist_list_obj = self.env['distribution.list']
        self.dist_list_line_obj = self.env['distribution.list.line']
        self.first_user = self.env.ref("distribution_list.first_user")
        self.first_user.write({
            'groups_id': [(4, self.env.ref("base.group_partner_manager").id)],
        })
        self.second_user = self.env.ref("distribution_list.second_user")
        self.partner_model = self.env.ref("base.model_res_partner")
        self.mail_template_model = self.env.ref("mail.model_mail_template")
        self.partner_id_field = self.env.ref("base.field_res_partner_id")

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
        distri_list_obj = distri_list_obj.sudo(user_creator.id)
        dist_list_line_values = {
            'name': 'employee',
            'domain': "[('employee', '=', True)]",
            'src_model_id': self.partner_model.id,
            'exclude': False,
            'bridge_field_id': self.partner_id_field.id,
        }
        distribution_list = distri_list_obj.create({
            'name': 'tee meeting',
            'company_id': user_creator.company_id.id,
            'dst_model_id': self.partner_model.id,
            'to_include_distribution_list_line_ids': [
                (0, False, dist_list_line_values),
            ],
        })
        distribution_list_line = distribution_list.\
            to_include_distribution_list_line_ids
        self.assertEquals(len(distribution_list_line), 1)
        with self.assertRaises(exceptions.AccessError) as e:
            distribution_list_line.sudo(user_no_access.id).read()
        self.assertIn("Document type: distribution.list.line, Operation: read",
                      e.exception.name)
        self.assertEquals(len(distribution_list), 1)
        with self.assertRaises(exceptions.AccessError) as e:
            distribution_list.sudo(user_no_access.id).read()
        self.assertIn("Document type: distribution.list, Operation: read",
                      e.exception.name)
        return

    def test_compute_distribution_list_ids(self):
        """

        :return:
        """
        partner_obj = self.partner_obj
        distri_list_obj = self.dist_list_obj
        distri_list_line_obj = self.dist_list_line_obj

        user_creator = self.first_user
        partner_obj = partner_obj.sudo(user_creator.id)
        customer = partner_obj.create({
            'active': True,
            'type': 'contact',
            'is_company': False,
            'lang': 'en_US',
            'child_ids': [],
            'customer': True,
            'user_ids': [],
            'name': 'customer',
            'category_id': [[6, False, []]],
            'company_id': user_creator.company_id.id,
        })

        supplier = partner_obj.create({
            'active': True,
            'type': 'contact',
            'is_company': False,
            'lang': 'en_US',
            'child_ids': [],
            'supplier': True,
            'user_ids': [],
            'name': 'supplier',
            'category_id': [[6, False, []]],
            'company_id': user_creator.company_id.id,
        })

        # create distribution_list_line and distribution_list with the first
        # user
        partner_obj = self.partner_model
        distri_list_line_obj = distri_list_line_obj.sudo(user_creator.id)
        distri_list_obj = distri_list_obj.sudo(user_creator.id)

        distribution_list = distri_list_obj.create({
            'name': str(uuid4()),
            'company_id': user_creator.company_id.id,
            'dst_model_id': partner_obj.id,
        })
        line1 = distri_list_line_obj.create({
            'name': str(uuid4()),
            'domain': "[('supplier', '=', True)]",
            'src_model_id': partner_obj.id,
            'company_id': user_creator.company_id.id,
            'distribution_list_id': distribution_list.id,
            'bridge_field_id': self.partner_id_field.id,
        })
        line2 = distri_list_line_obj.create({
            'name': 'employee_2',
            'domain': "[('customer', '=', True)]",
            'src_model_id': partner_obj.id,
            'company_id': user_creator.company_id.id,
            'distribution_list_id': distribution_list.id,
            'bridge_field_id': self.partner_id_field.id,
        })

        distribution_list_exclusion = distri_list_obj.create({
            'name': 'tee meeting 2',
            'company_id': user_creator.company_id.id,
            'dst_model_id': partner_obj.id,
        })
        line1.copy({
            'distribution_list_id': distribution_list_exclusion.id,
            'exclude': True,
            'name': str(uuid4()),
        })
        line2.copy({
            'distribution_list_id': distribution_list_exclusion.id,
            'exclude': True,
            'name': str(uuid4()),
        })
        distribution_list_cust_nosupl = distri_list_obj.create({
            'name': 'tee meeting 3',
            'company_id': user_creator.company_id.id,
            'dst_model_id': partner_obj.id,
        })
        line1.copy({
            'distribution_list_id': distribution_list_cust_nosupl.id,
            'exclude': True,
            'name': str(uuid4()),
        })
        line2.copy({
            'distribution_list_id': distribution_list_cust_nosupl.id,
            'exclude': False,
            'name': str(uuid4()),
        })

        targets = distribution_list._get_target_from_distribution_list()
        self.assertIn(customer.id, targets.ids)
        self.assertIn(supplier.id, targets.ids)

        targets = distribution_list_exclusion.\
            _get_target_from_distribution_list()
        self.assertNotIn(customer.id, targets.ids)
        self.assertNotIn(supplier.id, targets.ids)

        targets = distribution_list_cust_nosupl.\
            _get_target_from_distribution_list()
        self.assertIn(customer.id, targets.ids)
        return

    def test_not_safe_mode(self):
        """
        Test that excluded ids from excluded filters of distribution list are
        not removed from the resulting ids if they are included by filters
        into another distribution list
        ex:
        -------- DL1 ------------------ DL2 --------
        include   |  exclude || include  |  exclude
            A     |    B     ||    B     |    A
            -----------------------------------
            result: [A,B] with safe_mode = False
        """
        context = self.env.context.copy()
        context.update({
            'safe_mode': False,
        })
        partner_model = self.partner_obj.with_context(context)
        distri_list_obj = self.dist_list_obj.with_context(context)
        distri_list_line_obj = self.dist_list_line_obj.with_context(context)

        partner_name_1 = str(uuid4())
        partner_name_2 = str(uuid4())

        partner1 = partner_model.create({
            'name': partner_name_1,
        })
        partner2 = partner_model.create({
            'name': partner_name_2,
        })
        dst_model_id = self.partner_model

        include1_exclude2 = distri_list_obj.create({
            'name': str(uuid4()),
            'dst_model_id': dst_model_id.id,
        })
        distri_line_partner1 = distri_list_line_obj.create({
            'name': str(uuid4()),
            'domain': "[['name', '=', '%s']]" % partner_name_1,
            'src_model_id': dst_model_id.id,
            'distribution_list_id': include1_exclude2.id,
            'bridge_field_id': self.partner_id_field.id,
        })
        distri_line_partner2 = distri_list_line_obj.create({
            'name': str(uuid4()),
            'domain': "[['name', '=', '%s']]" % partner_name_2,
            'src_model_id': dst_model_id.id,
            'distribution_list_id': include1_exclude2.id,
            'exclude': True,
            'bridge_field_id': self.partner_id_field.id,
        })

        include2_exclude1 = distri_list_obj.create({
            'name': str(uuid4()),
            'dst_model_id': dst_model_id.id,
        })
        distri_line_partner1.copy({
            'distribution_list_id': include2_exclude1.id,
            'exclude': True,
        })
        distri_line_partner2.copy({
            'distribution_list_id': include2_exclude1.id,
            'exclude': False,
        })

        waiting_list = include2_exclude1 | include1_exclude2
        results = self.env['res.partner'].browse()
        for dist_list in waiting_list:
            results |= dist_list._get_target_from_distribution_list(
                safe_mode=False)
        self.assertEquals(len(waiting_list), 2)
        self.assertIn(partner1.id, results.ids)
        self.assertIn(partner2.id, results.ids)
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

        distribution_list1 = distribution_list_obj.create({
            'name': str(uuid4()),
            'dst_model_id': partner_model.id,
        })
        distribution_list2 = distribution_list_obj.create({
            'name': str(uuid4()),
            'dst_model_id': partner_model.id,
        })
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

        src_dist = dl_model.create({
            'name': 'src',
            'dst_model_id': dst_model_id.id,
        })
        dl_line_model.create({
            'name': str(uuid4()),
            'src_model_id': dst_model_id.id,
            'distribution_list_id': src_dist.id,
            'bridge_field_id': self.partner_id_field.id,
        })
        dl_line_model.create({
            'name': str(uuid4()),
            'src_model_id': dst_model_id.id,
            'distribution_list_id': src_dist.id,
            'exclude': True,
            'bridge_field_id': self.partner_id_field.id,
        })

        trg_dist = dl_model.create({
            'name': 'trg',
            'dst_model_id': dst_model_id.id,
        })
        dl_line_model.create({
            'name': str(uuid4()),
            'src_model_id': dst_model_id.id,
            'distribution_list_id': trg_dist.id,
            'bridge_field_id': self.partner_id_field.id,
        })
        trg_dist._complete_distribution_list(src_dist.ids)
        self.assertEquals(
            len(trg_dist.to_include_distribution_list_line_ids), 2)
        self.assertEquals(
            len(trg_dist.to_exclude_distribution_list_line_ids), 1)
        return

    def test_get_complex_distribution_list_ids(self):
        """
        Test that `get_complex_distribution_list_ids` return the correct ids
        when use a context with
        * more_filter
        * sort_by
        * field_alternative_object
        * field_main_object
        """
        partner_obj = self.partner_obj
        distri_list_obj = self.dist_list_obj
        distri_list_line_obj = self.dist_list_line_obj

        p9 = partner_obj.create({
            'name': 'p9',
        })
        p8 = partner_obj.create({
            'name': 'p8 more_filter filter_three',
            'parent_id': p9.id,
        })
        partner_obj.create({
            'name': 'p7 more_filter filter_three',
            'parent_id': p8.id,
        })

        p6 = partner_obj.create({
            'name': 'p6',
        })
        p5 = partner_obj.create({
            'name': 'p5',
        })
        p4 = partner_obj.create({
            'name': 'p4',
            'parent_id': p5.id,
        })
        partner_obj.create({
            'name': 'p3 filter_two',
            'parent_id': p6.id,
        })
        partner_obj.create({
            'name': 'p2 filter_one',
            'parent_id': p4.id,
        })
        partner_obj.create({
            'name': 'p1 filter_one',
            'parent_id': p4.id,
        })
        partner_model = self.partner_model
        dl = distri_list_obj.create({
            'name': 'get_complex_distribution_list_ids',
            'dst_model_id': partner_model.id,
            'bridge_field': 'parent_id',
        })
        distri_list_line_obj.create({
            'name': 'filter_one',
            'domain': "[('name', 'ilike', 'filter_one')]",
            'src_model_id': partner_model.id,
            'distribution_list_id': dl.id,
            'bridge_field_id': self.partner_id_field.id,
        })
        distri_list_line_obj.create({
            'name': 'filter_two',
            'domain': "[('name', 'ilike', 'filter_two')]",
            'src_model_id': partner_model.id,
            'distribution_list_id': dl.id,
            'bridge_field_id': self.partner_id_field.id,
        })
        distri_list_line_obj.create({
            'name': 'filter_three',
            'domain': "[('name', 'ilike', 'filter_three')]",
            'src_model_id': partner_model.id,
            'distribution_list_id': dl.id,
            'bridge_field_id': self.partner_id_field.id,
        })
        context = self.env.context.copy()
        context.update({
            'more_filter': [('name', '=', 'p4')],
            'sort_by': 'name desc',
            'field_alternative_object': 'company_id',
            'alternative_more_filter': [('parent_id', '=', False)],
            'field_main_object': 'parent_id',
        })
        mains, alternatives = dl.with_context(
            context)._get_complex_distribution_list_ids()
        self.assertEquals(
            mains.ids, p5.ids, 'Should have p5 partner has result')
        self.assertEquals(
            first(alternatives).id, 1,
            'Should have at least one company as alternative object')

        context.pop('more_filter')
        mains, alternatives = dl.with_context(
            context)._get_complex_distribution_list_ids()
        self.assertEquals(
            len(mains), 2, 'Should have 2 ids if no `more_filter`')

        context.update({
            'more_filter': [('name', '=', 'x23')],
        })
        mains, alternatives = dl.with_context(
            context)._get_complex_distribution_list_ids()
        self.assertFalse(
            mains,
            'With a "noway" domain and a target field name, '
            'should return no result')

        context.pop('field_main_object')
        primary_ids = dl.with_context(
            context)._get_target_from_distribution_list()
        mains, alternatives = dl.with_context(
            context)._get_complex_distribution_list_ids()
        self.assertEquals(
            mains, primary_ids,
            'With no target field name, should return the same result as '
            '"get_ids_from_distribution_list"')
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

        distribution_list = distri_list_obj.create({
            'name': 'tea meeting to copy',
            'dst_model_id': partner_model.id,
            'company_id': False,
        })
        distri_list_line_obj.create({
            'name': 'employee to copy',
            'domain': "[('employee', '=', True)]",
            'src_model_id': partner_model.id,
            'distribution_list_id': distribution_list.id,
            'bridge_field_id': self.partner_id_field.id,
        })

        distribution_list_copy = distribution_list.sudo(user.id).copy()
        self.assertEquals(
            distribution_list.dst_model_id.id,
            distribution_list_copy.dst_model_id.id)
        line_origin = distribution_list.to_include_distribution_list_line_ids
        line_cpy = distribution_list_copy.to_include_distribution_list_line_ids
        self.assertTrue(line_cpy)
        self.assertEquals(line_cpy.domain, line_origin.domain)
        self.assertEquals(line_cpy.exclude, line_origin.exclude)
        self.assertEquals(
            line_cpy.src_model_id.id, line_origin.src_model_id.id)
        return

    def test_mass_mailing(self):
        """
        Test that action is well returned with correct value required for
        a mass mailing
        """
        distribution_list_obj = self.dist_list_obj
        partner_model = self.partner_model

        dist_list = distribution_list_obj.create({
            'name': str(uuid4()),
            'dst_model_id': partner_model.id,
        })
        result = dist_list.mass_mailing()
        self.assertEqual(
            result.get('type'), 'ir.actions.act_window',
            "Should be an ir.actions.act_window ")
        self.assertEqual(
            result.get('res_model'), 'mail.compose.message',
            "This mass mailing is made with mail composer")
        # test context content
        context = result.get('context', {})
        self.assertEqual(
            context.get('default_composition_mode'), 'mass_mail',
            "Mass mailing must be launch into mass_mail mode")
        self.assertEqual(
            context.get('active_model'), 'res.partner',
            "Active model must be the same that the distribution list")
        self.assertEqual(
            context.get('default_distribution_list_id'), dist_list.id,
            "default_distribution_list_id must be the same that the "
            "distribution list's id")
        return

    def test_get_action_from_domain(self):
        """
        Test that action is well returned with correct value required for
        a `get_actions_from_domains`
        """
        distribution_list_obj = self.dist_list_obj
        partner_model = self.partner_model
        dist_list = distribution_list_obj.create({
            'name': str(uuid4()),
            'dst_model_id': partner_model.id,
        })
        result = dist_list.get_action_from_domains()
        self.assertEqual(result.get('type'), 'ir.actions.act_window',
                         "Should be an ir.actions.act_window ")
        self.assertEqual(result.get('res_model'), 'res.partner',
                         "Model should be the same than the distribution list")
        return
