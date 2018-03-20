# -*- coding: utf-8 -*-
# Copyright 2018 Acsone Sa/Nv
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import tempfile
import csv
import base64

from openerp import api
from openerp.osv import orm, fields
from openerp.tools.translate import _

from .export_csv_request import VIRTUAL_TARGET_REQUEST
from .export_csv_request import EMAIL_COORDINATE_REQUEST
from .export_csv_request import POSTAL_COORDINATE_REQUEST


def _get_utf8(data):
    if not data:
        return None
    return unicode(data).encode('utf-8', 'ignore')


class export_csv(orm.TransientModel):
    _name = 'export.csv'
    _description = 'Export CSV Wizard'

    _columns = {
        'export_file': fields.binary('Csv', readonly=True),
        'export_filename': fields.char('Export CSV Filename', size=128),
    }

    def _get_csv_rows(self, cr, uid, context=None):
        """
        Get the rows (header) for the specified model.
        """
        hdr = [
            _('Number'),
            _('Name'),
            _('Lastname'),
            _('Firstname'),
            _('Usual Lastname'),
            _('Usual Firstname'),
            _('Co-residency Line 1'),
            _('Co-residency Line 2'),
            _('Internal Instance'),
            _('Power Level'),
            _('State'),
            _('Reference'),
            _('Birth Date'),
            _('Gender'),
            _('Tongue'),
            _('Main Address'),
            _('Unauthorized Address'),
            _('Vip Address'),
            _('Street2'),
            _('Street'),
            _('Zip'),
            _('City'),
            _('Country Code'),
            _('Country'),
            _('Main Phone'),
            _('Unauthorized Phone'),
            _('Vip Phone'),
            _('Phone'),
            _('Main Mobile'),
            _('Unauthorized Mobile'),
            _('Vip Mobile'),
            _('Mobile'),
            _('Main Fax'),
            _('Unauthorized Fax'),
            _('Vip Fax'),
            _('Fax'),
            _('Main Email'),
            _('Unauthorized Email'),
            _('Vip Email'),
            _('Email'),
            _('Website'),
            _('Secondary Website'),
            _('Local voluntary'),
            _('Regional voluntary'),
            _('National voluntary'),
            _('Local only'),
        ]

        return [_get_utf8(col) for col in hdr]

    def _get_order_by(self, order_by):
        r_order_by = "ORDER BY p.id"
        if order_by:
            if order_by == "identifier" or order_by == "technical_name":
                r_order_by = "ORDER BY p.%s" % order_by
            else:
                r_order_by =\
                    "ORDER BY country_name, final_zip, p.technical_name"
        return r_order_by

    @api.cr_uid_context
    def _get_csv_values(self, cr, uid, obj, obfuscation, context=None):
        """
        Get the values of the specified obj taking into account the VIP
        obfuscation principle
        """

        export_values = [
            obj.get('identifier'),
            _get_utf8(obj.get('name')),
            _get_utf8(obj.get('lastname')),
            _get_utf8(obj.get('firstname')),
            _get_utf8(obj.get('usual_lastname')),
            _get_utf8(obj.get('usual_firstname')),
            _get_utf8(obj.get('printable_name')),
            _get_utf8(obj.get('co_residency')),
            _get_utf8(obj.get('instance')),
            _get_utf8(obj.get('power_name')),
            _get_utf8(obj.get('state')),
            _get_utf8(obj.get('reference')),
            obj.get('birth_date'),
            _get_utf8(obj.get('gender')),
            _get_utf8(obj.get('tongue')),
            obj.get('adr_main'),
            obj.get('adr_unauthorized'),
            obj.get('adr_vip'),
            obj.get('adr_vip') and obfuscation or _get_utf8(
                obj.get('street2')),
            obj.get('adr_vip') and obfuscation or _get_utf8(obj.get('street')),
            obj.get('adr_vip') and obfuscation or obj.get('final_zip'),
            obj.get('adr_vip') and obfuscation or _get_utf8(obj.get('city')),
            obj.get('country_code'),
            _get_utf8(obj.get('country_name')),
            obj.get('fix_main'),
            obj.get('fix_unauthorized'),
            obj.get('fix_vip'),
            obj.get('fix_vip') and obfuscation or _get_utf8(obj.get('fix')),
            obj.get('mobile_main'),
            obj.get('mobile_unauthorized'),
            obj.get('mobile_vip'),
            obj.get('mobile_vip') and obfuscation or _get_utf8(obj.get(
                'mobile')),
            obj.get('fax_main'),
            obj.get('fax_unauthorized'),
            obj.get('fax_vip'),
            obj.get('fax_vip') and obfuscation or _get_utf8(obj.get('fax')),
            obj.get('email_main'),
            obj.get('email_unauthorized'),
            obj.get('email_vip'),
            obj.get('email_vip') and obfuscation or _get_utf8(obj.get(
                'email')),
            _get_utf8(obj.get('website')),
            _get_utf8(obj.get('secondary_website')),
            _get_utf8(obj.get('local_voluntary')),
            _get_utf8(obj.get('regional_voluntary')),
            _get_utf8(obj.get('national_voluntary')),
            _get_utf8(obj.get('local_only')),
        ]
        return export_values

    def _prefetch_csv_datas(self, cr, uid, model, model_ids, context=None):
        if not model_ids:
            return
        if model == 'email.coordinate':
            query = """
            %s WHERE ec.id IN %%s
            """ % EMAIL_COORDINATE_REQUEST
        elif model == 'postal.coordinate':
            query = """
            %s WHERE pc.id IN %%s
            """ % POSTAL_COORDINATE_REQUEST
        elif model == 'virtual.target':
            query = """
            %s WHERE vt.id IN %%s
            """ % VIRTUAL_TARGET_REQUEST
        else:
            raise orm.except_orm(
                _('Error'),
                _('Model %s not supported for csv export!') % model)
        order_by = self._get_order_by(context.get('sort_by'))
        query = "%s %s" % (query, order_by)
        cr.execute(query, (tuple(model_ids),))
        for row in cr.dictfetchall():
            yield row

    def get_csv(self, cr, uid, model, model_ids, group_by=False, context=None):
        """
        Build a CSV file related to a coordinate model
        """
        tmp = tempfile.NamedTemporaryFile(
            prefix='Extract', suffix=".csv", delete=False)
        f = open(tmp.name, "r+")
        writer = csv.writer(f)
        hdr = self._get_csv_rows(cr, uid, context=context)
        writer.writerow(hdr)
        co_residencies = []
        if model_ids:
            state_ids = self.pool['membership.state'].search(
                cr, uid, [], context=context)
            states = self.pool['membership.state'].browse(
                cr, uid, state_ids, context=context)
            states = {st.id: st.name for st in states}
            country_ids = self.pool['res.country'].search(
                cr, uid, [], context=context)
            countries = self.pool['res.country'].browse(
                cr, uid, country_ids, context=context)
            countries = {cnt.id: cnt.name for cnt in countries}
            selections = self.pool['res.partner'].fields_get(
                cr, uid, allfields=['gender', 'tongue'], context=context)
            genders = {k: v for k, v in selections['gender']['selection']}
            tongues = {k: v for k, v in selections['tongue']['selection']}
            viper = self.pool['res.users'].has_group(
                cr, uid, 'mozaik_base.mozaik_res_groups_vip_reader')
            obfuscation = False if viper else 'VIP'
            for data in self._prefetch_csv_datas(
                    cr, uid, model, model_ids, context=context):
                if data.get('state_id'):
                    data['state'] = states[data['state_id']]
                if data.get('country_id'):
                    data['country_name'] = countries[data['country_id']]
                if data.get('gender'):
                    data['gender'] = genders.get(data['gender'])
                if data.get('tongue'):
                    data['tongue'] = tongues.get(data['tongue'])
                if model == 'postal.coordinate' and group_by:
                    # when grouping by co_residency, output only one row
                    # by co_residency
                    co_id = data.get('co_residency_id')
                    if co_id and co_id in co_residencies:
                        continue
                    co_residencies.append(co_id)
                export_values = self._get_csv_values(
                    cr, uid, data, obfuscation, context=context)
                assert len(hdr) == len(export_values)
                writer.writerow(export_values)
        f.close()
        f = open(tmp.name, "r")
        csv_content = f.read()
        f.close()
        return csv_content

    def export(self, cr, uid, ids, context=None):
        model = context.get('active_model', False)
        model_ids = context.get('active_ids', False)
        csv_content = self.get_csv(cr, uid, model, model_ids, context=context)

        csv_content = base64.encodestring(csv_content)

        self.write(cr, uid, ids[0],
                   {'export_file': csv_content,
                    'export_filename': 'Extract.csv'},
                   context=context)

        return {
            'name': 'Export Csv',
            'type': 'ir.actions.act_window',
            'res_model': 'export.csv',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(False, 'form')],
            'target': 'new',
        }
