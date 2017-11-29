# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestInvolvement(TransactionCase):

    def setUp(self):
        super(TestInvolvement, self).setUp()

    def test_involvment(self):
        """
        Check for creation of involvement when validating
        """
        # create an involvement category
        cat = self.env['partner.involvement.category'].create({
            'name': 'Les hommes viennent de Mars...',
            'code': 'Mars',
        })
        # create a membership request
        mr = self.env['membership.request'].create({
            'lastname': 'Venus',
            'involvement_category_ids': [(6, 0, [cat.id])],
        })
        # validate it
        mr.validate_request()
        partner = mr.partner_id
        # an involvement related to the choosen category is created
        self.assertEqual('Mars', partner.partner_involvement_ids.code)
        self.assertEqual(
            cat,
            partner.partner_involvement_ids.involvement_category_id)
        # make another membership request
        mrid = partner.button_modification_request()['res_id']
        mr = self.env['membership.request'].browse(mrid)
        # involvement categories are initialized with those of the partner
        self.assertEqual(
            partner.partner_involvement_ids.involvement_category_id,
            mr.involvement_category_ids)
        # create an involvement category
        cat = self.env['partner.involvement.category'].create({
            'name': 'Les femmes viennent de Venus...',
            'code': 'Venus',
        })
        # add it to the involvement categories
        mr.involvement_category_ids |= cat
        # validate the request
        mr.validate_request()
        # partner has now 2 involvements
        codes = partner.partner_involvement_ids.mapped('code')
        codes.sort()
        self.assertEqual(['Mars', 'Venus'], codes)
        self.assertEqual(
            partner.partner_involvement_ids.mapped('involvement_category_id'),
            mr.involvement_category_ids)
