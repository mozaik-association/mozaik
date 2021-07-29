# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions

from odoo.tests.common import TransactionCase


class TestCreateUserFromPartner(TransactionCase):

    def test_create_user_from_partner(self):
        """
        Test the creation of a user from a partner
        """
        wz_obj = self.env['create.user.from.partner']
        # get a company
        nouvelobs = self.browse_ref('mozaik_person.res_partner_demo_01')
        # get defaults
        res = wz_obj.with_context(active_id=nouvelobs.id).default_get(['nok'])
        self.assertEqual('company', res['nok'])
        nouvelobs.toggle_active()
        res = wz_obj.with_context(active_id=nouvelobs.id).default_get(['nok'])
        self.assertEqual('active', res['nok'])
        res = wz_obj.with_context(
            active_id=self.env.user.partner_id.id).default_get(['nok'])
        self.assertEqual('user', res['nok'])
        with self.assertRaises(exceptions.UserError):
            res = wz_obj.with_context().default_get(['nok'])
        # create a role
        role = self.env['res.users.role'].create({'name': 'Abracadabra'})
        # get a partner and a group
        dany = self.browse_ref('mozaik_person.res_partner_demo_03')
        # build and execute a wizard
        wz = wz_obj.with_context(active_id=dany.id).new({
            'login': 'Bof!',
            'role_id': role.id,
        })
        user = wz.create_user_from_partner()
        self.assertEqual(dany.user_ids, user)
        self.assertEqual('Bof!', user.login)
        self.assertIn(user, role.line_ids.mapped('user_id'))
