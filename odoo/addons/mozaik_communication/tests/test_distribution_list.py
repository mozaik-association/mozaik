# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from uuid import uuid4
import psycopg2
from odoo.tests.common import SavepointCase
from odoo.fields import first


class TestDistributionList(SavepointCase):

    def setUp(self):
        super(TestDistributionList, self).setUp()
        self.user_obj = self.env['res.users']
        self.partner_obj = self.env['res.partner']
        self.dl_obj = self.env['distribution.list']
        self.mail_obj = self.env['mail.mail']
        self.int_instance_obj = self.env['int.instance']
        self.ec_obj = self.env['email.coordinate']
        self.pc_obj = self.env['postal.coordinate']
        self.virtrg_obj = self.env['virtual.target']
        self.evr_lst = self.env.ref('mozaik_communication.everybody_list')
        self.partner_model = self.env.ref("base.model_res_partner")
        self.company = self.env.ref('base.main_company')
        self.officier_group = self.env.ref(
            'mozaik_base.mozaik_res_groups_officer')
        self.partner = self.env.ref(
            'mozaik_communication.res_partner_nouvelobs')
        self.partner_thierry = self.env.ref(
            "mozaik_communication.res_partner_thierry")
        self.usr = self.create_an_officier()

    def create_an_officier(self):
        name = str(uuid4())
        # create the partner
        vals = {
            'name': name,
        }
        partner = self.partner_obj.create(vals)
        default_instance = self.int_instance_obj.get_default()

        # create the user
        vals = {
            'name': name,
            'login': name,
            'partner_id': partner,
            'company_id': self.company.id,
            'groups_id': [(4, self.officier_group.id, False)],
            'int_instance_m2m_ids': [(6, 0, default_instance.ids)],
        }
        return self.user_obj.create(vals)

    def test_only_owner_forward(self):
        email = 'alibaba@test.eu'
        # set email after to avoid MailDeliveryException
        vals = {
            'partner_id': self.usr.partner_id.id,
            'email': email,
        }
        mail_coord = self.ec_obj.create(vals)
        # take a DL where user is not an owner nor an allowed partner
        dist_list = self.evr_lst
        msg = {
            'email_from': "<%s>" % email,
            'subject': 'test',
            'body': 'body',
        }
        dist_list._distribution_list_forwarding(msg)
        domain = [
            ('res_id', '=', mail_coord.id),
            ('model', '=', 'email.coordinate'),
        ]
        mails = self.mail_obj.search()
        self.assertFalse(mails)
        # add user to the owner
        vals = {
            'res_users_ids': [(6, 0, self.usr.ids)]
        }
        dist_list.write(vals)
        dist_list._distribution_list_forwarding(msg)
        mails = self.mail_obj.search(domain)
        self.assertTrue(mails)
        mails.unlink()
        # remove user from owners but add it as allowed partner
        vals = {
            'res_users_ids': [(3, self.usr.id, False)],
            'res_partner_ids': [(6, 0, self.usr.partner_id.ids)],
        }
        dist_list.write(vals)
        dist_list._distribution_list_forwarding(msg)
        mails = self.mail_obj.search(domain)
        self.assertTrue(mails)
        mails.unlink()
        # take a legal person without a responsible user
        partner = self.partner
        # add it an email coordinate
        vals = {
            'partner_id': partner.id,
            'email': 'emmanuel.vals.noway@nouvelobs.eu',
        }
        self.ec_obj.create(vals)
        # use it as a sender
        msg.update({
            'email_from': vals.get('email'),
        })
        # make the legal person an allowed partner of the DL
        vals = {
            'res_partner_ids': [(4, partner.id, False)],
        }
        dist_list.write(vals)
        dist_list._distribution_list_forwarding(msg)
        mails = self.mail_obj.search(domain)
        self.assertFalse(mails)
        # add it a responsible user
        vals = {
            'responsible_user_id': self.usr.id,
        }
        partner.write(vals)
        dist_list._distribution_list_forwarding(msg)
        mails = self.mail_obj.search(domain)
        self.assertTrue(mails)
        mails.unlink()
        # inactive the user
        self.usr.active = False
        dist_list._distribution_list_forwarding(msg)
        mails = self.mail_obj.search(domain)
        self.assertFalse(mails)
        # reactive the user
        self.usr.active = True
        # but with the same ec as the legal person
        vals = {
            'partner_id': self.usr.partner_id.id,
            'email': 'emmanuel.vals.noway@nouvelobs.eu',
        }
        self.ec_obj.create(vals)
        dist_list._distribution_list_forwarding(msg)
        mails = self.mail_obj.search(domain)
        self.assertFalse(mails)

    def test_newsletter_code_unique(self):
        vals = {
            'name': 'Newsletter Sample 1',
            'code': 'SAMPLE1',
            'newsletter': True,
        }
        self.dl_obj.create(vals)
        vals = {
            'name': 'Newsletter Sample 2',
            'code': 'SAMPLE1',
            'newsletter': True,
        }
        # Disable error into logs
        previous_log = self.env.cr._default_log_exceptions
        self.env.cr._default_log_exceptions = False
        with self.assertRaises(psycopg2.IntegrityError):
            self.dl_obj.create(vals)
        self.env.cr._default_log_exceptions = previous_log

    def test_notify_owner_on_alias_change(self):
        dl_name = str(uuid4())
        default_instance = first(self.usr.int_instance_m2m_ids)
        # set email after to avoid MailDeliveryException
        vals = {
            'partner_id': self.usr.partner_id.id,
            'email': 'sacha.distel@example.com',
        }
        self.ec_obj.create(vals)
        vals = {
            'name': dl_name,
            'int_instance_id': default_instance.id,
            'dst_model_id': self.partner_model.id,
            'mail_forwarding': True,
            'alias_name': 'xxx',
            'res_users_ids': [(6, False, [self.env.uid, self.usr.id])]
        }
        dist_list = self.dl_obj.create(vals)
        vals = {
            'alias_name': "yyy",
        }
        dist_list.write(vals)
        # owner should notified
        mails = self.mail_obj.search([
            ('subject', 'ilike', dl_name),
            ('recipient_ids', 'in', self.usr.partner_id.id),
        ])
        self.assertEqual(len(mails), 1)

    def test_complex_distribution_list_ids(self):
        # create a vip email
        partner_thierry = self.partner_thierry
        mail_coord = self.ec_obj.create({
            'partner_id': partner_thierry,
            'email': 'x23@example.com',
            'vip': True,
        })
        dist_list = self.evr_lst
        officer_uid = self.usr.id
        # virtual_target, admin
        mains, alternatives = dist_list._get_complex_distribution_list_ids()
        search_result_recs = self.virtrg_obj.search([('identifier', '!=', 0)])
        self.assertFalse(alternatives)
        self.assertEqual(mains, search_result_recs)
        domain = [
            ('identifier', '!=', 0),
            '&',
            '|',
            ('email', '=', False),
            ('email', '!=', 'VIP'),
            '|',
            ('postal', '=', False),
            ('postal', '!=', 'VIP'),
        ]
        # virtual_target, other user
        mains, = dist_list.sudo(
            officer_uid)._get_complex_distribution_list_ids()
        search_result_recs = self.virtrg_obj.sudo(officer_uid).search(domain)
        self.assertEqual(mains, search_result_recs)
        context = self.env.context.copy()
        context.update(
            main_object_field='email_coordinate_id',
            main_object_domain=[],
            main_target_model='email.coordinate',
            alternative_object_field='postal_coordinate_id',
            alternative_object_domain=[('email_coordinate_id', '=', False)],
            alternative_target_model='postal.coordinate',
        )
        # email_coordinate_id, postal_coordinate_id, admin
        mains, alternatives = dist_list.with_context(
            context)._get_complex_distribution_list_ids()
        self.virtrg_obj = self.virtrg_obj.with_context(context)
        self.assertIn(mail_coord, mains)
        domain = [
            ('identifier', '!=', 0),
            ('email_coordinate_id', '!=', False),
        ]
        mail_coordinates = self.virtrg_obj.search(domain).mapped(
            "email_coordinate_id")
        self.assertEqual(set(mains), set(mail_coordinates))
        postal_coordinates = self.virtrg_obj.search([
            ('identifier', '!=', 0),
            ('email_coordinate_id', '=', False),
            ('postal_coordinate_id', '!=', False),
        ]).mapped("postal_coordinate_id")
        self.assertEqual(set(alternatives), set(postal_coordinates))
        inactives = self.virtrg_obj.search([('active', '=', False)])
        mains_vip = mains.filtered("vip")
        alternatives_vip = alternatives.filtered("vip")
        # email_coordinate_id, postal_coordinate_id, other user
        mains, alternatives = dist_list.sudo(
            officer_uid)._get_complex_distribution_list_ids()
        self.assertNotIn(mail_coord, mains)
        mail_coord = self.virtrg_obj.sudo(officer_uid).search([
            ('identifier', '!=', 0),
            ('email_coordinate_id', '!=', False),
        ]).mapped("email_coordinate_id")
        self.assertEqual(mains, mail_coord - mains_vip)
        postal_coord = self.virtrg_obj.sudo(officer_uid).search([
            ('identifier', '!=', 0),
            ('email_coordinate_id', '=', False),
            ('postal_coordinate_id', '!=', False),
        ]).mapped("postal_coordinate_id")
        self.assertEqual(alternatives, postal_coord - alternatives_vip)
        context.update(
            main_object_field='id',
            main_object_domain=[],
            main_target_model='virtual.target',
            active_test=False,
        )
        dist_list = dist_list.with_context(context)
        # virtual target, admin, inactive
        other_mains, = dist_list._get_complex_distribution_list_ids()
        self.assertEqual(other_mains - inactives, mains)
        return
