# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import psycopg2

from anybox.testing.openerp import SharedSetupTransactionCase

from openerp.addons.mozaik_base import testtool


class TestPartnerInvolvementCategory(SharedSetupTransactionCase):

    _data_files = (
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml',
        '../../mozaik_mandate/tests/data/mandate_data.xml',
    )

    _module_ns = 'mozaik_involvement_followup'

    def test_involvement_category_integrity_1(self):
        # create a category with negative deadline rule: NOK
        vals = {
            'name': 'Le tour du monde en 80 jours',
            'nb_deadline_days': -80,
        }
        with testtool.disable_log_error(self.cr):
            self.assertRaises(
                psycopg2.IntegrityError,
                self.env['partner.involvement.category'].create, vals)

    def test_involvement_category_integrity_2(self):
        mc_id = self.ref('%s.mc_secretaire_regional' % self._module_ns)
        # create a category without deadline rule but with a mandate: NOK
        vals = {
            'name': 'Le tour du monde en 80 jours',
            'nb_deadline_days': 0,
            'mandate_category_id': mc_id,
        }
        with testtool.disable_log_error(self.cr):
            self.assertRaises(
                psycopg2.IntegrityError,
                self.env['partner.involvement.category'].create, vals)

    def test_involvement_category_onchange_deadline_rule(self):
        mc_id = self.ref('%s.mc_secretaire_regional' % self._module_ns)
        vals = {
            'name': 'Le tour du monde en 80 jours',
            'nb_deadline_days': 0,
            'mandate_category_id': mc_id,
        }
        cat = self.env['partner.involvement.category'].new(vals)
        # change deadline rule to null
        cat._onchange_nb_deadline_days()
        # mandate category must be null
        self.assertFalse(cat.mandate_category_id)
        return
