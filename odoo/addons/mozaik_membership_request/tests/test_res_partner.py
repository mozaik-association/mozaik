# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import uuid
from datetime import date
from dateutil.relativedelta import relativedelta

from openerp.osv import orm
from anybox.testing.openerp import SharedSetupTransactionCase


class test_partner(SharedSetupTransactionCase):

    _data_files = (
        # load the partner
        '../../mozaik_base/tests/data/res_partner_data.xml',
        # load structures
        '../../mozaik_structure/tests/data/structure_data.xml',
        '../../mozaik_address/tests/data/reference_data.xml',
        '../../mozaik_address/tests/data/address_data.xml',
    )

    _module_ns = 'mozaik_membership'

    def setUp(self):
        super(test_partner, self).setUp()

        self.mr_obj = self.registry('membership.request')
        self.partner_obj = self.registry('res.partner')
        self.ms_obj = self.registry('membership.state')
        self.ml_obj = self.registry('membership.line')
        self.prd_obj = self.registry('product.template')
        self.imd_obj = self.registry['ir.model.data']

        self.partner1 = self.browse_ref(
            '%s.res_partner_thierry' % self._module_ns)

        self.partner2 = self.browse_ref(
            '%s.res_partner_fgtb' % self._module_ns)

        self.user_model = self.registry('res.users')
        self.partner_jacques_id = self.ref(
            '%s.res_partner_jacques' % self._module_ns)
        self.group_fr_id = self.ref('mozaik_base.mozaik_res_groups_reader')

    def test_button_modification_request(self):
        """
        Check that a `membership.request` object is well created with
        the datas of the giving partner.
        test raise if partner does not exist
        """
        mr_obj, partner, cr, uid, context = self.mr_obj,\
            self.partner1, self.cr, self.uid, {}
        fr = self.ref('base.fr')
        partner.write({
            'regional_voluntary': True,
            'local_only': True,
            'nationality_id': fr,
        })
        res = self.partner_obj.button_modification_request(
            cr, uid, [partner.id], context=context)
        mr = mr_obj.browse(cr, uid, res['res_id'], context=context)
        postal_coordinate_id = partner.postal_coordinate_id or False
        mobile_coordinate_id = partner.mobile_coordinate_id or False
        fix_coordinate_id = partner.fix_coordinate_id or False
        email_coordinate_id = partner.email_coordinate_id or False
        int_instance_id = partner.int_instance_id or False
        birth_date = partner.birth_date
        day = False
        month = False
        year = False
        if partner.birth_date:
            datas = partner.birth_date.split('-')
            day = datas[2]
            month = datas[1]
            year = datas[0]
        self.assertEqual(mr.membership_state_id, partner.membership_state_id)
        self.assertEqual(mr.result_type_id, partner.membership_state_id)
        self.assertEqual(mr.identifier, partner.identifier, '[memb.req.]\
        identifier should be the same that [partner]identifier ')
        self.assertEqual(mr.lastname, partner.lastname, '[memb.req.]lastname\
        should be the same that [partner]lastname ')
        self.assertEqual(mr.firstname, partner.firstname, '[memb.req.]\
        firstname should be the same that [partner]firstname ')
        self.assertEqual(mr.gender, partner.gender, '[memb.req.]gender should \
        be the same that [partner]gender ')
        self.assertEqual(mr.birth_date, birth_date, '[memb.req.]birth_date \
        should be the same that [partner]birth_date ')
        self.assertEqual(mr.day, day and int(day), '[memb.req.]day should be \
        the same that [partner]day ')
        self.assertEqual(mr.month, month and int(month), '[memb.req.]month \
        should be the same that [partner]month ')
        self.assertEqual(mr.year, year and int(year), '[memb.req.]year should\
        be the same that [partner]year ')
        self.assertEqual(mr.is_update, True, '[memb.req.]is_update should be \
        True')
        self.assertEqual(mr.country_id and mr.country_id.id or False,
                         postal_coordinate_id and postal_coordinate_id.
                         address_id.country_id.id, '[memb.req.]country_id \
                         should be the same that [partner]country_id ')
        self.assertEqual(mr.address_local_street_id and
                         mr.address_local_street_id.id or False,
                         postal_coordinate_id and postal_coordinate_id.
                         address_id.address_local_street_id.id,
                         '[memb.req.]address_local_street_id should be the \
                         same that [partner]address_local_street_id ')
        self.assertEqual(mr.street_man, postal_coordinate_id and
                         postal_coordinate_id.address_id.street_man,
                         '[memb.req.]street_man should be the same that\
                         [partner]street_man ')
        self.assertEqual(mr.street2, postal_coordinate_id and
                         postal_coordinate_id.address_id.street2,
                         '[memb.req.]street2 should be the same that \
                         [partner]street2 ')
        self.assertEqual(mr.address_local_zip_id and
                         mr.address_local_zip_id.id or False,
                         postal_coordinate_id and postal_coordinate_id.
                         address_id.address_local_zip_id.id,
                         '[memb.req.]address_local_zip_id should be the same\
                         that [partner]address_local_zip_id ')
        self.assertEqual(mr.zip_man, postal_coordinate_id and
                         postal_coordinate_id.address_id.zip_man,
                         '[memb.req.]zip_man should be the same that \
                         [partner]zip_man')
        self.assertEqual(mr.town_man, postal_coordinate_id and
                         postal_coordinate_id.address_id.town_man,
                         '[memb.req.]town_man should be the same that \
                         [partner]town_man')
        self.assertEqual(mr.box, postal_coordinate_id and
                         postal_coordinate_id.address_id.box,
                         '[memb.req.]box should be the same that [partner]box')
        self.assertEqual(mr.number, postal_coordinate_id and
                         postal_coordinate_id.address_id.number,
                         '[memb.req.]number should be the same that \
                         [partner]number')
        self.assertEqual(mr.mobile, mobile_coordinate_id and
                         mobile_coordinate_id.phone_id.name,
                         '[memb.req.]mobile should be the same that \
                         [partner]mobile')
        self.assertEqual(mr.phone, fix_coordinate_id and
                         fix_coordinate_id.phone_id.name,
                         '[memb.req.]phone should be the same that \
                         [partner]phone')
        self.assertEqual(mr.mobile_id and mr.mobile_id.id or False,
                         mobile_coordinate_id and mobile_coordinate_id.
                         phone_id.id, '[memb.req.]mobile_id should be the \
                         same that [partner]mobile_id ')
        self.assertEqual(mr.phone_id and mr.phone_id.id or False,
                         fix_coordinate_id and fix_coordinate_id.phone_id.id,
                         '[memb.req.]phone_id should be the same that \
                         [partner]phone_id')
        self.assertEqual(mr.email, email_coordinate_id and
                         email_coordinate_id.email, '[memb.req.]email should \
                         be the same that [partner]email')
        self.assertEqual(mr.address_id and mr.address_id.id or False,
                         postal_coordinate_id and
                         postal_coordinate_id.address_id.id,
                         '[memb.req.]address_id should be the same that \
                         [partner]address_id ')
        self.assertEqual(mr.int_instance_id and mr.int_instance_id.id or
                         False, int_instance_id and int_instance_id.id,
                         '[memb.req.]int_instance_id should be the same that \
                         [partner]int_instance_id ')
        self.assertEqual(mr.interests_m2m_ids or [[6, False, []]],
                         [[6, False, partner.interests_m2m_ids and
                           [interest.id for interest in
                            partner.interests_m2m_ids] or []]],
                         '[memb.req.]interests_m2m_ids should be the same \
                         that [partner]interests_m2m_ids ')
        self.assertEqual(mr.partner_id and mr.partner_id.id, partner.id,
                         '[memb.req.]partner_id should be the same that \
                         [partner]partner_id ')
        self.assertEqual(mr.competencies_m2m_ids or [[6, False, []]],
                         [[6, False, partner.competencies_m2m_ids and
                           [competence.id for competence in
                            partner.competencies_m2m_ids] or []]],
                         '[memb.req.]competencies_m2m_ids should be the same \
                         that [partner]competencies_m2m_ids ')
        self.assertEqual(mr.local_voluntary, partner.local_voluntary)
        self.assertEqual(mr.regional_voluntary, True)
        self.assertEqual(mr.local_only, True)
        self.assertEqual(mr.national_voluntary, partner.national_voluntary)
        self.assertEqual(mr.nationality_id, partner.nationality_id)
