
# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from anybox.testing.openerp import SharedSetupTransactionCase
from email.utils import formataddr


class TestMassFunction(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        'data/communication_data.xml',
    )

    _module_ns = 'mozaik_communication'

    def test_onchange_subject_and_template(self):
        cr, uid, context = self.cr, self.uid, {'in_mozaik_user': True}
        evr_lst_id = self.ref('%s.everybody_list' % self._module_ns)
        mfct_obj = self.registry('distribution.list.mass.function')
        vals = {
            'trg_model': 'email.coordinate',
            'e_mass_function': 'email_coordinate_id',
            'distribution_list_id': evr_lst_id,
        }
        wiz_id = mfct_obj.create(cr, uid, vals, context)
        wiz = mfct_obj.browse(cr, uid, wiz_id)
        self.assertFalse(wiz.mass_mailing_name)
        subject = 'Le livre de la jungle'
        values = mfct_obj.onchange_subject(
            cr, uid, [wiz_id], subject, wiz.mass_mailing_name)
        mfct_obj.write(cr, uid, [wiz_id], values['value'])
        self.assertEqual(subject, wiz.mass_mailing_name)
        values = mfct_obj.onchange_subject(
            cr, uid, [wiz_id], 'La guerre des étoiles', wiz.mass_mailing_name)
        self.assertFalse(values)
        return

    def test_save_as_template(self):
        mfct_obj = self.env['distribution.list.mass.function']
        evr_lst_id = self.ref('%s.everybody_list' % self._module_ns)
        vals = {
            'trg_model': 'email.coordinate',
            'e_mass_function': 'email_coordinate_id',
            'distribution_list_id': evr_lst_id,
            'subject': 'TEST1',
            'body': '<p>hello</p>',
        }
        wizard = mfct_obj.with_context({'in_mozaik_user': True}).create(vals)
        wizard.save_as_template()
        self.assertTrue(bool(wizard.email_template_id))
        self.assertEqual(wizard.email_template_id.subject, vals['subject'])
        self.assertEqual(wizard.email_template_id.body_html, vals['body'])
        return

    def test_email_from(self):
        '''
        Check for:
        * partner_from_id content and default value
        * email_from computed value
        '''
        # create 2 new users
        partner_obj = self.env['res.partner']
        vals = {
            'name': 'Bob',
            'email': 'bob@vandersteen.be',
        }
        p1 = partner_obj.create(vals)
        vals = {
            'name': 'Bobette',
            'email': 'bobette@vandersteen.be',
            'is_company': True,
        }
        p2 = partner_obj.create(vals)
        # add a partner_id and a res_partner_m2m_ids to a distribution list
        dl = self.browse_ref('%s.everybody_list' % self._module_ns)
        vals = {
            'partner_id': p1.id,
            'res_partner_m2m_ids': [(6, 0, [p2.id])],
        }
        dl.write(vals)
        # from now, allowed "From" are:
        # - the parner of the list: bob
        # - authorized companies specified on the list: bobette
        # - the user because he is an owner of the list: admin

        # check for possible "From" choices
        mfct_obj = self.env['distribution.list.mass.function'].with_context(
            {'active_model': 'distribution.list', 'active_id': dl.id})
        partners = mfct_obj._get_partner_from()
        p_ids = [p1.id, p2.id, self.env.user.partner_id.id]
        self.assertEqual(set(partners.ids), set(p_ids))
        # check for default value
        def_from = mfct_obj._get_default_partner_from_id()
        self.assertEqual(def_from, self.env.user.partner_id)
        # check for email_from
        vals = {
            'partner_from_id': p2.id,
            'partner_name': 'Le roi Arthur',
        }
        wizard = mfct_obj.create(vals)
        email = formataddr((vals['partner_name'], p2.email))
        self.assertEqual(email, wizard.email_from)

        # check for possible "From" choices simulating a wizard reload
        mfct_obj = mfct_obj.with_context(
            {'active_model': mfct_obj._name, 'active_id': wizard.id})
        partners = mfct_obj._get_partner_from()
        self.assertEqual(set(partners.ids), set(p_ids))

        vals = {
            'partner_id': False,
            'res_users_ids': [(5, 0, 0)],
        }
        dl.write(vals)
        p2.is_company = False
        # from now, allowed "From" are: nobody
        partners = mfct_obj._get_partner_from()
        # check for possible "From" choices
        self.assertFalse(partners)
        return
