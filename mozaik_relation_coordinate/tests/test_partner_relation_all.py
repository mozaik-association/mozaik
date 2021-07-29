# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import fields
from odoo.tests.common import SavepointCase


class TestPartnerRelationAll(SavepointCase):

    def setUp(self):
        super().setUp()
        self.ec_id = self.browse_ref('mozaik_email.email_coordinate_pauline')
        self.pc_id = self.ref('mozaik_address.postal_coordinate_3')
        self.relation = self.env['res.partner.relation'].create({
            'left_partner_id': self.ec_id.partner_id.id,
            'type_id': self.ref('partner_multi_relation.rel_type_assistant'),
            'right_partner_id': self.ref(
                'mozaik_coordinate.res_partner_thierry'),
        })
        relid = self.relation.id
        relid *= self.env['res.partner.relation.all']._get_padding()
        self.rel = self.env['res.partner.relation.all'].browse(relid)
        assert self.rel.active
        self.inverse_type_id = self.rel.type_selection_id.browse(
            self.rel.type_selection_id.id + 1)

    def test_toggle_active(self):
        """
        Check for toggle_active inheriting:
        * if record is active: date_end is set to yesterday
        * if record is inative: date_end is reset
        * in all case active is recomputed regarding date_end
        """
        y = (
            datetime.date.today() - datetime.timedelta(days=1)).strftime(
                fields.DATE_FORMAT)
        # Inactivate relation
        self.rel.toggle_active()
        # record is now inactive with a date_end
        self.assertFalse(self.rel.active)
        self.assertEqual(y, self.rel.date_end)
        # Reactivate relation
        self.rel.toggle_active()
        # record is active again without date_end
        self.assertTrue(self.rel.active)
        self.assertFalse(self.rel.date_end)
        return

    def test_correct_vals(self):
        """
        Check for values sanitizing:
        * if relation type is inverse, coordinates are removed
        * not otherwise
        """
        # is_inverse = False
        vals = {
            'email_coordinate_id': self.ec_id,
            'postal_coordinate_id': self.pc_id,
        }
        type_selection = self.rel.type_selection_id
        values = self.rel._correct_vals(vals, type_selection)
        # dictionary is unchanged
        self.assertTrue(all([
            values['email_coordinate_id'],
            values['postal_coordinate_id'],
        ]))
        # is_inverse = False
        values = self.rel._correct_vals(vals, self.inverse_type_id)
        # dictionary has lost its coordinates
        self.assertFalse(any([
            'email_coordinate_id' in values,
            'postal_coordinate_id' in values,
        ]))
        return

    def test_onchange_type_selection_id(self):
        """
        Check for is_inverse value when changing type_selection_id
        """
        # create a memory relation
        relation = self.env['res.partner.relation.all'].new({
            'this_partner_id': self.rel.this_partner_id.id,
            'other_partner_id': self.rel.other_partner_id.id,
        })
        relation.onchange_type_selection_id()
        # without type, is_inverse is false
        self.assertFalse(relation.is_inverse)
        # add it an inverse relation
        relation.type_selection_id = self.inverse_type_id
        relation.onchange_type_selection_id()
        # is_inverse now true
        self.assertTrue(relation.is_inverse)
        # change it with a non inverse relation
        relation.type_selection_id = self.rel.type_selection_id
        relation.onchange_type_selection_id()
        # is_inverse is false again
        self.assertFalse(relation.is_inverse)
        return
