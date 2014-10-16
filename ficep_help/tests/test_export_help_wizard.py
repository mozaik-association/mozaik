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
import base64
from lxml import etree as ET

from anybox.testing.openerp import SharedSetupTransactionCase

_logger = logging.getLogger(__name__)


class test_export_help_wizard(object):
    _data_files = ('data/help_test_data.xml',)

    _module_ns = 'ficep_help'

    def createPage(self, pageName, imgXmlId=False):
        imgId = False
        if imgXmlId:
            imgId = self.ref('%s.%s' % (self._module_ns, imgXmlId))

        rootNode = ET.Element('t')
        rootNode.attrib['name'] = pageName
        rootNode.attrib['t-name'] = "website.%s" % pageName
        tNode = ET.SubElement(rootNode, 't')
        tNode.attrib['t-call'] = "website.layout"
        structDivNode = ET.SubElement(tNode, 'div')
        structDivNode.attrib['class'] = "oe_structure oe_empty"
        structDivNode.attrib['id'] = "wrap"
        sectionNode = ET.SubElement(structDivNode, 'section')
        sectionNode.attrib['class'] = "mt16 mb16"
        containerNode = ET.SubElement(sectionNode, 'div')
        containerNode.attrib['class'] = "container"
        rowNode = ET.SubElement(containerNode, 'div')
        rowNode.attrib['class']= "row"
        bodyDivNode = ET.SubElement(rowNode, 'div')
        bodyDivNode.attrib['class'] = "col-md-12 text-center mt16 mb32"
        h2Node = ET.SubElement(bodyDivNode, 'h2')
        h2Node.attrib['style'] = "font-family: 'Helvetica Neue', Helvetica,"\
                                 " Arial, sans-serif; color: rgb(51, 51, 51);"\
                                 " text-align: left;"
        h2Node.text = "Test Sample Title"
        if imgId:
            imgDivNode = ET.SubElement(bodyDivNode, 'div')
            imgDivNode.attrib['style'] = "text-align: left;"
            imgNode = ET.SubElement(imgDivNode, 'img')
            imgNode.attrib['class'] = "img-thumbnail"
            imgNode.attrib['src'] = "/website/image?field=datas&"\
                                    "model=ir.attachment&id=" + str(imgId)
            imgDivNode = ET.SubElement(bodyDivNode, 'div')
            imgDivNode.attrib['style'] = "text-align: left;"
            imgNode = ET.SubElement(imgDivNode, 'img')
            imgNode.attrib['class'] = "img-thumbnail"
            imgNode.attrib['src'] = "/website/image/ir.attachment/" \
                                    "%s_ccc838d/datas" % str(imgId)
        arch = ET.tostring(rootNode, encoding='utf-8', xml_declaration=False)
        view_id = self.registry('ir.ui.view').create(self.cr, self.uid, {
            'name': pageName,
            'type': 'qweb',
            'arch': arch,
            'page': True,
        })
        return view_id

    def setUp(self):
        super(test_export_help_wizard, self).setUp()
        self.pageName = False
        self.imgXmlId = False
        self.pageTemplate = False

    def test_export_help(self):
        '''
            Export help data
        '''
        self.createPage(pageName=self.pageName, imgXmlId=self.imgXmlId)

        wizardPool = self.registry('export.help.wizard')
        wizId = wizardPool.create(
                            self.cr,
                            self.uid,
                            {},
                            context={})
        wizardPool.export_help(self.cr, self.uid, [wizId], context={})
        wizard = wizardPool.browse(self.cr, self.uid, [wizId], context={})
        xmlData = base64.decodestring(wizard.data)

        parser = ET.XMLParser(remove_blank_text=True)
        rootXml = ET.XML(xmlData, parser=parser)

        xPath = ".//template[@id='website.%s']" % self.pageName
        templateNodeList = rootXml.findall(xPath)
        self.assertEqual(len(templateNodeList), 1)
        self.assertNotIn("website.", templateNodeList[0].attrib['name'])

        if self.imgXmlId:
            xPath = ".//record[@id='%s_img_01']" % self.pageName
            imgNodeList = rootXml.findall(xPath)
            self.assertEqual(len(imgNodeList), 1)

            for imgElem in templateNodeList[0].iter('img'):
                imgSrc = imgElem.get('src')
                if '/ir.attachment/' in imgSrc:
                    self.assertIn("/ir.attachment/%s_img_02|" \
                                  % self.pageName, imgSrc)
                else:
                    self.assertIn("id=%s_img_01" % self.pageName, imgSrc)

        if self.pageTemplate:
            xPath = ".//template[@id='website.%s_snippet']" % self.pageName
            templateNodeList = rootXml.findall(xPath)
            self.assertEqual(len(templateNodeList), 1)
            self.assertNotIn("website.", templateNodeList[0].attrib['name'])


class test_export_help_with_image(test_export_help_wizard,
                                  SharedSetupTransactionCase):
    def setUp(self):
        super(test_export_help_with_image, self).setUp()
        self.pageName = 'mozaik-help-test-page'
        self.imgXmlId = 'test_img_1'


class test_export_help_template(test_export_help_wizard,
                                  SharedSetupTransactionCase):
    def setUp(self):
        super(test_export_help_template, self).setUp()
        self.pageName = 'mozaik-help-template-test'
        self.pageTemplate = True
