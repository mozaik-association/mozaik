# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from anybox.testing.openerp import SharedSetupTransactionCase


class TestPartnerInvolvement(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_thesaurus/tests/data/thesaurus_data.xml',
        'data/partner_involvement_category_data.xml',
    )

    _module_ns = 'mozaik_person'

    def setUp(self):
        super(TestPartnerInvolvement, self).setUp()
        # during tests, suspend_security hook has to be manually registered
        self.registry('ir.rule')._register_hook(self.cr)
        self.paul = self.browse_ref(
            '%s.res_partner_paul' % self._module_ns)
        self.euro2000 = self.browse_ref(
            '%s.partner_involvement_category_euro2000' % self._module_ns)

    def test_add_interests_on_involvement_creation(self):
        '''
        Check for interests propagation when creating an involvement
        '''
        for term in self.euro2000.interests_m2m_ids:
            self.assertNotIn(term, self.paul.interests_m2m_ids)
        involvement = self.env['partner.involvement'].create({
            'partner_id': self.paul.id,
            'involvement_category_id': self.euro2000.id,
        })
        for term in self.euro2000.interests_m2m_ids:
            self.assertIn(term, self.paul.interests_m2m_ids)
        return

