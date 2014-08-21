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
import os
import sys
from lxml import etree as ET

from anybox.testing.openerp import SharedSetupTransactionCase

_logger = logging.getLogger(__name__)


class test_export_help_wizard(SharedSetupTransactionCase):
    _data_files = ()

    _module_ns = 'ficep_help'

    def setUp(self):
        super(test_export_help_wizard, self).setUp()

    def test_export_help_wizard(self):
        '''
            Export help data
        '''
        module = sys.modules[self.__module__]
        base_path = os.path.dirname(module.__file__)
        path = '../data/help_data.xml'
        path = path.split('/')
        path.insert(0, base_path)
        path = os.path.join(*path)
        reference_file = open(path, 'r')
        reference_data = reference_file.read()
        wizard_pool = self.registry('export.help.wizard')
        wiz_id = wizard_pool.create(
                            self.cr,
                            self.uid,
                            {},
                            context={})
        wizard_pool.export_help(self.cr, self.uid, [wiz_id], context={})
        wizard = wizard_pool.browse(self.cr, self.uid, [wiz_id], context={})
        exported_data = base64.decodestring(wizard.data)

        parser = ET.XMLParser(remove_blank_text=True)
        exported_xml = ET.XML(exported_data, parser=parser)
        reference_xml = ET.XML(reference_data, parser=parser)

        exported_string = ET.tostring(exported_xml).replace('\n', ' ')
        reference_string = ET.tostring(reference_xml).replace('\n', ' ')

        self.assertEqual(exported_string, reference_string)
