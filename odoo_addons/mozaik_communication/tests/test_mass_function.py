
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
