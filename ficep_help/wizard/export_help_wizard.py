# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm, fields

from lxml import etree as ET
import xml.dom.minidom as minidom
import base64
import time
from os.path import expanduser


class export_help_wizard(orm.TransientModel):
    _name = "export.help.wizard"
    _description = 'Export Ficep Help'

    def _get_qweb_views_data(self, cr, uid, context=None):
        view_data_list = self.pool.get('ir.ui.view').search_read(
                                            cr,
                                            uid,
                                            [('type', '=', 'qweb'),
                                             ('name',
                                              'like',
                                              'website.ficep-help-%')],
                                            ['arch'],
                                            context=context)
        xml_to_export = ET.Element('openerp')
        data_node = ET.SubElement(xml_to_export, 'data')

        for view_data in view_data_list:
            parser = ET.XMLParser(remove_blank_text=True)
            root = ET.XML(view_data['arch'], parser=parser)
            root.tag = 'template'
            template_id = root.attrib['t-name']
            root.attrib.pop('t-name')
            root.attrib['id'] = template_id
            data_node.append(root)

        rough_string = ET.tostring(xml_to_export, encoding='utf-8',
                                   xml_declaration=True)
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8')

    _columns = {
        'data': fields.binary('XML', readonly=True),
        'export_filename': fields.char('Export XML Filename', size=128),
    }

    def export_help(self, cr, uid, ids, context=None):
        """
        Export all Qweb views related to help online in a Odoo
        data XML file
        """
        context = context or {}

        out = base64.encodestring(self._get_qweb_views_data(cr,
                                                            uid,
                                                            context=context))

        self.write(cr, uid, ids,
                   {'data': out,
                    'export_filename': 'help_data.xml'},
                   context=context)

        return {
            'name': 'Help Online Export',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(False, 'form')],
            'target': 'new',
        }

    def auto_backup(self, cr, uid, ids=False, context=None):
        """
            Export data to a file on home directory of user
        """
        if not context:
            context = {}
        if not ids:
            ids = self.search(cr, uid, [], context=context)

        xml_data = self._get_qweb_views_data(cr, uid, context)

        timestr = time.strftime("%Y%m%d-%H%M%S")
        home = expanduser("~")
        filename = '%s/ficep_help_online_backup-%s.xml' % (home, timestr)
        backup_file = open(filename,
                           'w')
        backup_file.write(xml_data)
        backup_file.close
