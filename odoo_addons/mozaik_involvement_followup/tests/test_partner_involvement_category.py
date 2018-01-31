# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import psycopg2

from anybox.testing.openerp import SharedSetupTransactionCase

from openerp.exceptions import ValidationError
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
            'name': 'Blanche neige et les 7 nains',
        }
        ic = self.env['partner.involvement.category'].create(vals)
        vals = {
            'name': 'Le tour du monde en 80 jours',
            'nb_deadline_days': 0,
            'mandate_category_id': mc_id,
            'involvement_category_ids': [(6, 0, [ic.id])],
        }
        cat = self.env['partner.involvement.category'].new(vals)
        # change deadline rule to null
        cat._onchange_nb_deadline_days()
        # mandate category and follow-up categories must be false
        self.assertFalse(cat.mandate_category_id)
        self.assertFalse(cat.involvement_category_ids)
        return

    def test_involvement_category_followup_constrains(self):
        vals = {
            'name': 'Blanche neige et les 7 nains',
            'nb_deadline_days': 1,
        }
        ic3 = self.env['partner.involvement.category'].create(vals)
        vals = {
            'name': 'Blanche neige et les 7 vilains',
            'nb_deadline_days': 1,
            'involvement_category_ids': [(6, 0, [ic3.id])],
        }
        ic2 = self.env['partner.involvement.category'].create(vals)
        vals = {
            'name': 'Blanche neige et les 7 mains',
            'nb_deadline_days': 1,
            'involvement_category_ids': [(6, 0, [ic2.id])],
        }
        ic1 = self.env['partner.involvement.category'].create(vals)
        # make a recursion loop through involvement_category_ids => NOK
        self.assertRaises(
            ValidationError,
            ic3.write, {'involvement_category_ids': [(6, 0, [ic1.id])]})
        # make ic3 a petition => NOK
        self.assertRaises(
            ValidationError,
            ic3.write, {'involvement_type': 'petition'})
        # clean ic3
        ic3.write({
            'involvement_type': False, 'involvement_category_ids': [(5, 0, 0)]
        })
        # make ic1 a petition => OK
        ic1.write({'involvement_type': 'petition'})
        return
