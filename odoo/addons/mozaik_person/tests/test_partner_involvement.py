# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import psycopg2
from datetime import datetime, timedelta

from anybox.testing.openerp import SharedSetupTransactionCase

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from openerp.exceptions import ValidationError

from openerp.addons.mozaik_base import testtool


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
        self.env['partner.involvement'].create({
            'partner_id': self.paul.id,
            'involvement_category_id': self.euro2000.id,
        })
        for term in self.euro2000.interests_m2m_ids:
            self.assertIn(term, self.paul.interests_m2m_ids)
        return

    def test_multi(self):
        """
        Check for multiple involvements
        """
        # create an involvement category
        cat = self.env['partner.involvement.category'].create({
            'name': 'Buvons un coup ma serpette...',
        })
        # create an involvement
        involvement = self.env['partner.involvement'].create({
            'partner_id': self.paul.id,
            'involvement_category_id': cat.id,
        })
        # check for effective_time
        self.assertFalse(involvement.effective_time)
        # copy it: NOK
        self.assertRaises(ValidationError, involvement.copy)
        # allow miltiple involvements
        cat.allow_multi = True
        # check for effective_time
        self.assertTrue(involvement.effective_time)
        involvement.unlink()
        # create a new involvement
        now = (datetime.now() + timedelta(hours=-1)).strftime(DATETIME_FORMAT)
        involvement = self.env['partner.involvement'].create({
            'partner_id': self.paul.id,
            'involvement_category_id': cat.id,
            'effective_time': now,
        })
        # copy it: OK
        involvement.copy()
        # create an already existing involvement: NOK
        with testtool.disable_log_error(self.cr):
            self.assertRaises(
                psycopg2.IntegrityError,
                self.env['partner.involvement'].create,
                {
                    'partner_id': self.paul.id,
                    'involvement_category_id': cat.id,
                    'effective_time': now,
                })
        return

    def test_onchange_type(self):
        """
        Check for allow_multiple when changing involvment type
        """
        # create an involvement category
        cat = self.env['partner.involvement.category'].new({
            'name': 'Semeur, vaillants du rêve...',
        })
        # Change type to donation
        cat.involvement_type = 'donation'
        cat._onchange_involvement_type()
        self.assertTrue(cat.allow_multi)
        # Change type to another type
        cat.involvement_type = 'voluntary'
        cat._onchange_involvement_type()
        self.assertFalse(cat.allow_multi)
