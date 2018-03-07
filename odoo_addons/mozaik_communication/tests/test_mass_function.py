
# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from anybox.testing.openerp import SharedSetupTransactionCase


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
        self.assertEqual(wizard.email_template_id.model_id.model, 'email.coordinate')
