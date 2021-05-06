# -*- coding: utf-8 -*-
# Copyright 2018 Acsone Sa/Nv
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import tempfile
import csv
import base64

from openerp import api
from openerp.osv import orm, fields
from openerp.tools.translate import _


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
            _('Lastname'),
            _('Firstname'),
            _('Internal Instance'),
            _('State'),
            _('Reference'),
            _('Gender'),
            _('Street'),
            _('Zip'),
            _('City'),
            _('Country'),
            _('Phone'),
            _('Mobile'),
            _('Email'),
            _('Website'),
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
            _get_utf8(obj.get('lastname')),
            _get_utf8(obj.get('firstname')),
            _get_utf8(obj.get('instance')),
            _get_utf8(obj.get('state')),
            _get_utf8(obj.get('reference')),
            _get_utf8(obj.get('gender')),
            obj.get('adr_vip') and obfuscation or _get_utf8(obj.get('street')),
            obj.get('adr_vip') and obfuscation or obj.get('final_zip'),
            obj.get('adr_vip') and obfuscation or _get_utf8(obj.get('city')),
            _get_utf8(obj.get('country_name')),
            obj.get('fix_vip') and obfuscation or _get_utf8(obj.get('fix')),
            obj.get('mobile_vip') and obfuscation or _get_utf8(obj.get(
                'mobile')),
            obj.get('email_vip') and obfuscation or _get_utf8(obj.get(
                'email')),
            _get_utf8(obj.get('website')),
        ]
        return export_values

    def _prefetch_csv_datas(self, cr, uid, model, model_ids, context=None):
        queries_obj = self.pool['export.csv.queries']
        if not model_ids:
            return
        if model == 'email.coordinate':
            query = """
            %s WHERE ec.id IN %%s
            """ % queries_obj.email_coordinate_request(cr, uid)
        elif model == 'postal.coordinate':
            query = """
            %s WHERE pc.id IN %%s
            """ % queries_obj.postal_coordinate_request(cr, uid)
        elif model == 'virtual.target':
            query = """
            %s WHERE vt.id IN %%s
            """ % queries_obj.virtual_target_request(cr, uid)
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
