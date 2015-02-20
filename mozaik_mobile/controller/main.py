# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_mobile, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_mobile is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_mobile is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_mobile.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import http
from openerp.addons.web.controllers import main

from openerp.addons.mozaik_base.base_tools import format_email
from openerp.addons.mozaik_person.res_partner import available_genders, \
    available_civil_status, available_tongues


class Mobile(main.Home):

    # partner per page
    _PPG = 10

    @http.route(['/partner_mobile',
                '/partner_mobile/page/<int:page>'],
                auth='public', website=True)
    def index_partner_mobile(self, page=1, search=False, value=False, **kw):
        """
        Index provides the list of partner
        Manage a pager too
        """
        def create_pager(url, partner_count):
            pager = http.request.website.pager(
                url=url, total=partner_count, page=page,
                step=self._PPG, scope=4, url_args=kw)
            return pager

        cr, uid, domain = http.request.cr, http.request.uid, []
        context = http.request.context
        url = "/partner_mobile"
        mobile_obj = http.request.registry['virtual.mobile.partner']
        partner_obj = http.request.registry['res.partner']

        if search and value:
            if search == 'email':
                value = format_email(value)
            domain = [(search, 'ilike', value)]
            kw['search'] = search
            kw['value'] = value

        mobile_ids = list(set(mobile_obj.search(
            cr, uid, domain, context=context)))
        pager = create_pager(url, len(mobile_ids))

        domain = [('id', 'in', mobile_ids)]
        partner_ids = partner_obj.search(
            cr, uid, domain, offset=pager['offset'], limit=self._PPG,
            order='display_name', context=context)
        partners = partner_obj.browse(cr, uid, partner_ids, context=context)

        return http.request.render(
            'mozaik_mobile.mobile_index', {
                "pager": pager,
                "partners": partners,
            })

    @http.route('/partner_view/<model("res.partner"):partner>/',
                auth='public', website=True)
    def show_partner(self, partner, **kw):
        """
        :type partner: browse record of partner
        :rparam: render of qweb with all main informations of a partner
        """
        cr, uid, = http.request.cr, http.request.uid
        context = http.request.context
        # get email_coordinate records
        email_coordinate_obj = http.request.registry['email.coordinate']
        email_coordinate_ids = email_coordinate_obj.search(
            cr, uid, [('partner_id', '=', partner.id)], context=context)
        email_coordinate_records = email_coordinate_obj.browse(
            cr, uid, email_coordinate_ids, context=context)
        # get phone_coordinate records
        phone_coordinate_obj = http.request.registry['phone.coordinate']
        phone_coordinate_ids = phone_coordinate_obj.search(
            cr, uid, [('partner_id', '=', partner.id)], context=context)
        phone_coordinate_records = phone_coordinate_obj.browse(
            cr, uid, phone_coordinate_ids, context=context)
        # get postal_coordinate records
        postal_coordinate_obj = http.request.registry['postal.coordinate']
        postal_coordinate_ids = postal_coordinate_obj.search(
            cr, uid, [('partner_id', '=', partner.id)], context=context)
        postal_coordinate_records = postal_coordinate_obj.browse(
            cr, uid, postal_coordinate_ids, context=context)
        # get state_mandate records
        sta_mandate_obj = http.request.registry['sta.mandate']
        sta_mandate_ids = sta_mandate_obj.search(
            cr, uid, [('partner_id', '=', partner.id)], context=context)
        sta_mandate_records = sta_mandate_obj.browse(
            cr, uid, sta_mandate_ids, context=context)
        # get internal_mandate records
        int_mandate_obj = http.request.registry['int.mandate']
        int_mandate_ids = int_mandate_obj.search(
            cr, uid, [('partner_id', '=', partner.id)], context=context)
        int_mandate_records = int_mandate_obj.browse(
            cr, uid, int_mandate_ids, context=context)
        # get state_mandate records
        ext_mandate_obj = http.request.registry['ext.mandate']
        ext_mandate_ids = ext_mandate_obj.search(
            cr, uid, [('partner_id', '=', partner.id)], context=context)
        ext_mandate_records = ext_mandate_obj.browse(
            cr, uid, ext_mandate_ids, context=context)
        # relation
        relation_obj = http.request.registry['partner.relation']
        # subject relation
        subject_relation_ids = relation_obj.search(
            cr, uid, [('subject_partner_id', '=', partner.id)],
            context=context)
        subject_relation_records = relation_obj.browse(
            cr, uid, subject_relation_ids, context=context)
        # object relation
        object_relation_ids = relation_obj.search(
            cr, uid, [('object_partner_id', '=', partner.id)], context=context)
        object_relation_records = relation_obj.browse(
            cr, uid, object_relation_ids, context=context)

        to_show_phone_coo = False
        for phone_coo in phone_coordinate_records:
            if not phone_coo.is_main:
                to_show_phone_coo = True
                break
        vals = {
            'partner': partner,
            'to_show_phone_coo': to_show_phone_coo,
            'email_coordinates': email_coordinate_records,
            'postal_coordinates': postal_coordinate_records,
            'phone_coordinates': phone_coordinate_records,
            'available_genders': available_genders,
            'available_tongues': available_tongues,
            'available_civil_status': available_civil_status,
            'subject_relation_records': subject_relation_records,
            'object_relation_records': object_relation_records,
            'sta_mandate_records': sta_mandate_records,
            'int_mandate_records': int_mandate_records,
            'ext_mandate_records': ext_mandate_records,
        }
        return http.request.render('mozaik_mobile.show_partner', vals)

    @http.route('/partner_search_form/', auth='public', website=True)
    def partner_search_form(self, **kw):
        """
        Get qweb form to make a search
        """
        return http.request.render('mozaik_mobile.partner_search_form')
