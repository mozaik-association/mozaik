# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import csv
import base64
from io import StringIO
from odoo import api, exceptions, models, fields, _


class ExportCsv(models.TransientModel):
    _name = 'export.csv'
    _description = 'Export CSV Wizard'

    export_file = fields.Binary(
        string="CSV",
        readonly=True,
    )
    export_filename = fields.Char(
        string="Export CSV filename",
    )

    @api.model
    def _get_csv_rows(self):
        """
        Get the rows (header) for the specified model.
        :return: list of str
        """
        header = [
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
            _('Language'),
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
        return header

    @api.model
    def _get_order_by(self, order_by):
        """
        Based on the given order_by, build the order by
        :param order_by: str
        :return: str
        """
        r_order_by = "ORDER BY p.id"
        if order_by in ['identifier', 'technical_name']:
            r_order_by = "ORDER BY p.%s" % order_by
        elif order_by:
            r_order_by = "ORDER BY country_name, final_zip, p.technical_name"
        return r_order_by

    @api.model
    def _get_csv_values(self, values, obfuscation):
        """
        Get the values of the specified obj taking into account the VIP
        obfuscation principle
        :param values: dict
        :param obfuscation: str
        :return: list of str
        """
        keys = [
            'identifier',
            'name',
            'lastname',
            'firstname',
            'usual_lastname',
            'usual_firstname',
            'printable_name',
            'co_residency',
            'instance',
            'power_name',
            'state',
            'reference',
            'birthdate_date',
            'gender',
            'lang',
            'adr_main',
            'adr_unauthorized',
            'adr_vip',
            'adr_vip' and obfuscation or 'street2',
            'adr_vip' and obfuscation or 'street',
            'adr_vip' and obfuscation or 'final_zip',
            'adr_vip' and obfuscation or 'city',
            'country_code',
            'country_name',
            'fix_main',
            'fix_unauthorized',
            'fix_vip',
            'fix_vip' and obfuscation or 'fix',
            'mobile_main',
            'mobile_unauthorized',
            'mobile_vip',
            'mobile_vip' and obfuscation or 'mobile',
            'fax_main',
            'fax_unauthorized',
            'fax_vip',
            'fax_vip' and obfuscation or 'fax',
            'email_main',
            'email_unauthorized',
            'email_vip',
            'email_vip' and obfuscation or 'email',
            'website',
            'secondary_website',
            'local_voluntary',
            'regional_voluntary',
            'national_voluntary',
            'local_only',
        ]
        export_values = [values.get(k) for k in keys]
        return export_values

    @api.model
    def _prefetch_csv_datas(self, model, model_ids):
        """

        :param model:
        :param model_ids:
        :return:
        """
        queries_obj = self.env['export.csv.queries']
        if not model_ids:
            return
        if model == 'email.coordinate':
            query = """
            %s WHERE ec.id IN %%s
            """ % queries_obj.email_coordinate_request()
        elif model == 'postal.coordinate':
            query = """
            %s WHERE pc.id IN %%s
            """ % queries_obj.postal_coordinate_request()
        elif model == 'virtual.target':
            query = """
            %s WHERE vt.id IN %%s
            """ % queries_obj.virtual_target_request()
        else:
            raise exceptions.UserError(
                _('Model %s not supported for csv export!') % model)
        order_by = self._get_order_by(self._context.get('sort_by'))
        query = "%s %s" % (query, order_by)
        self.env.cr.execute(query, (tuple(model_ids),))
        for row in self.env.cr.dictfetchall():
            yield row

    @api.model
    def get_csv(self, model, model_ids, group_by=False):
        """
        Build a CSV file related to a coordinate model
        :param model: str
        :param model_ids: list of int
        :param group_by: str
        :return: str
        """
        with StringIO() as memory_file:
            writer = csv.writer(memory_file)
            headers = self._get_csv_rows()
            writer.writerow(headers)
            co_residencies = []
            if model and model_ids:
                states = self.env['membership.state'].search([])
                states = {st.id: st.name for st in states}
                countries = self.env['res.country'].search([])
                countries = {cnt.id: cnt.name for cnt in countries}
                selections = self.env['res.partner'].fields_get(
                    allfields=['gender', 'lang'])
                genders = {k: v for k, v in selections['gender']['selection']}
                tongues = {k: v for k, v in selections['tongue']['selection']}
                viper = self.env['res.users'].has_group(
                    'mozaik_coordinate.res_groups_coordinate_vip_reader')
                obfuscation = 'VIP'
                if viper:
                    obfuscation = False
                for data in self._prefetch_csv_datas(model, model_ids):
                    if data.get('state_id'):
                        data['state'] = states.get(data['state_id'])
                    if data.get('country_id'):
                        data['country_name'] = countries.get(
                            data['country_id'])
                    if data.get('gender'):
                        data['gender'] = genders.get(data['gender'])
                    if data.get('lang'):
                        data['lang'] = tongues.get(data['lang'])
                    if model == 'postal.coordinate' and group_by:
                        # when grouping by co_residency, output only one row
                        # by co_residency
                        co_id = data.get('co_residency_id')
                        if co_id and co_id in co_residencies:
                            continue
                        co_residencies.append(co_id)
                    export_values = self._get_csv_values(data, obfuscation)
                    assert len(headers) == len(export_values)
                    writer.writerow(export_values)
            csv_content = memory_file.getvalue()
        return csv_content

    @api.multi
    def export(self):
        self.ensure_one()
        context = self._context
        model = context.get('active_model', False)
        model_ids = context.get('active_ids', False)
        csv_content = self.get_csv(model, model_ids)

        csv_content = base64.encodestring(csv_content)

        self.write({
            'export_file': csv_content,
            'export_filename': 'Extract.csv',
        })

        return {
            'name': 'Export Csv',
            'type': 'ir.actions.act_window',
            'res_model': 'export.csv',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
