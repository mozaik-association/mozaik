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
import logging
from lxml import etree as ET
import xml.dom.minidom as minidom
import base64
import time
import copy
from os.path import expanduser

from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)


class export_help_wizard(orm.TransientModel):
    _name = "export.help.wizard"
    _description = 'Export Ficep Help'

    def _get_qweb_views_data(self, cr, uid, context=None):
        view_data_list = self.pool.get('ir.ui.view').search_read(
                                            cr,
                                            uid,
                                            [('type', '=', 'qweb'),
                                             ('page', '=', True),
                                             ('name',
                                              'like',
                                              'ficep-help-%')],
                                            ['arch', 'name'],
                                            order='name',
                                            context=context)
        xml_to_export = ET.Element('openerp')
        data_node = ET.SubElement(xml_to_export, 'data')

        for view_data in view_data_list:
            parser = ET.XMLParser(remove_blank_text=True)
            root = ET.XML(view_data['arch'], parser=parser)

            root.tag = 'template'
            template_id = root.attrib.pop('t-name')
            root.attrib['name'] = view_data['name'].replace('website.', '')
            root.attrib['id'] = template_id
            root.attrib['page'] = 'True'

            i_img = 0
            img_model = 'ir.attachment'

            for img_elem in root.iter('img'):
                if img_model in img_elem.get('src'):
                    i_img += 1
                    xml_id = "%s_img_%s" % \
                        (root.attrib['name'], str(i_img).rjust(2, '0'))
                    img_src = img_elem.get('src')
                    attach_id = False
                    if 'id=' in img_src:
                        id_pos = img_src.index('id=') + 3
                        attach_id = img_elem.get('src')[id_pos:]
                        new_src = img_src.replace(attach_id, xml_id)
                    else:
                        fragments = img_src.split('ir.attachment/')
                        attach_id, trail = fragments[1].split('_', 1)
                        new_src = "/website/image/ir.attachment/%s|%s" % \
                            (xml_id, trail)

                    if not attach_id:
                        continue
                    img_ids = self.pool.get(img_model).search(cr,
                                                              uid,
                                                              [('id', '=',
                                                                attach_id)],
                                                              context=context)
                    if len(img_ids) == 0:
                        continue
                    image = self.pool.get(img_model).browse(cr,
                                                            uid,
                                                            int(attach_id),
                                                            context=context)
                    img_node = ET.SubElement(data_node, 'record')
                    img_elem.attrib['src'] = new_src
                    img_node.attrib['id'] = xml_id
                    img_node.attrib['model'] = img_model
                    field_node = ET.SubElement(img_node, 'field')
                    field_node.attrib['name'] = "datas"
                    field_node.text = str(image.datas)
                    field_node = ET.SubElement(img_node, 'field')
                    field_node.attrib['name'] = "index_content"
                    field_node.text = str(image.index_content)
                    field_node = ET.SubElement(img_node, 'field')
                    field_node.attrib['name'] = "datas_fname"
                    field_node.text = image.datas_fname
                    field_node = ET.SubElement(img_node, 'field')
                    field_node.attrib['name'] = "name"
                    field_node.text = image.name
                    field_node = ET.SubElement(img_node, 'field')
                    field_node.attrib['name'] = "res_model"
                    field_node.text = image.res_model
                    field_node = ET.SubElement(img_node, 'field')
                    field_node.attrib['name'] = "mimetype"
                    field_node.text = image.mimetype
                    data_node.append(img_node)

            # Remove http:// site prefix from href url
            for a_elem in root.iter('a'):
                if not a_elem.get('href'):
                    continue
                href = a_elem.get('href')
                if not href.startswith('http:'):
                    continue
                if '/page/ficep-help-' not in href:
                    continue
                trail = href.split('/page/ficep-help-', 1)[1]
                a_elem.attrib['href'] = '/page/ficep-help-%s' % trail

            data_node.append(root)

            if root.attrib['name'].startswith('ficep-help-template'):
                page = copy.deepcopy(root)
                snippet = ET.Element('template')
                snippet.attrib['id'] = template_id + '_snippet'
                snippet.attrib['inherit_id'] = 'website.snippets'
                snippet.attrib['name'] = root.attrib['name']
                xpath = ET.SubElement(snippet, 'xpath')
                xpath.attrib['expr'] = "//div[@id='snippet_structure']"
                xpath.attrib['position'] = 'inside'
                main_div = ET.SubElement(xpath, 'div')

                thumbnail = ET.SubElement(main_div, 'div')
                thumbnail.attrib['class'] = 'oe_snippet_thumbnail'
                img = ET.SubElement(thumbnail, 'img')
                img.attrib['class'] = 'oe_snippet_thumbnail_img'
                src = '/ficep_help/static/src/img/snippet/snippet_thumbs.png'
                img.attrib['src'] = src
                span = ET.SubElement(thumbnail, 'span')
                span.attrib['class'] = 'oe_snippet_thumbnail_title'
                span.text = root.attrib['name'].replace('ficep-help-', '')

                body = ET.SubElement(main_div, 'section')
                body.attrib['class'] = 'oe_snippet_body mt_simple_snippet'

                template = page.find(".//div[@id='wrap']")

                for node in template.getchildren():
                    body.append(node)

                data_node.append(snippet)

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
